from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.user import AuthService
import logging

logger = logging.getLogger("devanchor.dependencies.auth")

async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Dependency to retrieve the authenticated user from a JWT token."""
    logger.info("Extracting current user from Authorization header")
    token = authorization.replace("Bearer ", "")
    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(token)
        logger.info(f"Authenticated user: {user.username}")
        return user
    except HTTPException as e:
        logger.error(f"Authentication failed: {e.status_code}: {e.detail}")
        raise