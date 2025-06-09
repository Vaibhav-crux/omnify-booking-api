from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.jwt_utils import decode_token
from app.database.models.users import User
from app.utils.constants import ErrorMessages
from app.auth.permissions import check_permissions, normalize_path
import logging

logger = logging.getLogger("devanchor.middleware.auth")

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce JWT authentication and role-based permissions for non-public APIs."""
    public_routes = [
        ("/api/v1/health", "GET"),       # Health check
        ("/api/v1/users", "POST"),       # Signup
        ("/api/v1/users/login", "POST"), # Login
        ("/api/v1/roles", "GET"),        # List roles
        ("/api/v1/roles", "POST"),       # Create role
        ("/api/v1/auth/refresh", "POST"),# Refresh token
    ]

    async def dispatch(self, request: Request, call_next):
        # Check if the request matches a public route
        path = request.url.path
        method = request.method
        if any(route_path == path and route_method == method for route_path, route_method in self.public_routes):
            logger.debug(f"Skipping authentication for public route: {method} {path}")
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header")
            raise HTTPException(status_code=401, detail=ErrorMessages.UNAUTHORIZED)

        token = auth_header.replace("Bearer ", "").strip()
        if not token:
            logger.warning("Empty token provided in Authorization header")
            raise HTTPException(status_code=401, detail=ErrorMessages.UNAUTHORIZED)

        # Basic token format validation
        if len(token.split(".")) != 3:
            logger.warning("Invalid JWT token format: incorrect number of segments")
            raise HTTPException(status_code=401, detail=ErrorMessages.INVALID_TOKEN)

        try:
            # Decode token and extract user_id
            payload = decode_token(token)
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Token missing user_id")
                raise HTTPException(status_code=401, detail=ErrorMessages.INVALID_TOKEN)

            # Fetch user from database
            user = await User.get_or_none(id=user_id).prefetch_related("user_roles__role")
            if not user:
                logger.warning(f"User not found for id: {user_id}")
                raise HTTPException(status_code=401, detail=ErrorMessages.INVALID_TOKEN)

            # Attach user to request state
            request.state.user = user
            logger.debug(f"Authenticated user: {user.email}")

            # Check permissions based on user roles
            user_roles = [ur.role.name for ur in user.user_roles]
            normalized_path = normalize_path(path)
            await check_permissions(normalized_path, method, user_roles)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", extra={"token": "REDACTED"}, exc_info=True)
            raise HTTPException(status_code=401, detail=ErrorMessages.INVALID_TOKEN)

        return await call_next(request)

async def get_current_user(request: Request) -> User:
    user = getattr(request.state, "user", None)
    if not user:
        logger.warning("No authenticated user found in request state")
        raise HTTPException(status_code=401, detail=ErrorMessages.UNAUTHORIZED)
    return user

def add_auth_middleware(app):
    app.add_middleware(AuthMiddleware)