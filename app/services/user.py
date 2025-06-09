from app.database.models.users import User
from app.database.models.refresh_tokens import RefreshToken
from app.database.models.roles import Role
from app.database.models.user_roles import UserRole
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserResponse, RoleResponse, RefreshRequest
from tortoise.exceptions import IntegrityError
from fastapi import HTTPException
from app.utils.password_utils import get_password_hash, verify_password
from app.utils.jwt_utils import create_access_token, create_refresh_token, decode_token
from datetime import datetime, timedelta, timezone
from app.utils.constants import ErrorMessages
import logging

logger = logging.getLogger("devanchor.services.users")

async def create_user(user_data: UserCreate) -> UserResponse:
    try:
        user_dict = user_data.dict()
        user_dict["passwordHash"] = get_password_hash(user_dict.pop("password"))  # Hash the password

        user = await User.create(**user_dict)
        logger.info(f"User created: {user.email}")

        # Assign 'client' role
        client_role = await Role.get_or_none(name="client")
        if not client_role:
            logger.error("Client role not found during user creation")
            raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)
        await UserRole.create(
            user=user,
            role=client_role,
            description="Default client role assignment",
            status="active"
        )
        logger.info(f"Assigned 'client' role to user: {user.email}")

        # Generate access token
        access_token = create_access_token({"sub": str(user.id)})

        # Generate and store refresh token
        refresh_token = create_refresh_token({"sub": str(user.id)})
        await RefreshToken.create(
            user=user,
            token=refresh_token,
            expiresAt=datetime.now(timezone.utc) + timedelta(days=7),
            revoked=datetime.now(timezone.utc) + timedelta(days=30),
            status="active"
        )
        logger.info(f"Tokens generated for user: {user.email}")

        # Fetch roles for response
        user_roles = await user.user_roles.all().prefetch_related("role")
        roles = [
            RoleResponse(
                id=ur.role.id,
                name=ur.role.name,
                description=ur.role.description,
                status=ur.role.status
            ) for ur in user_roles
        ]

        # Return user with tokens and roles
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            status=user.status,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt,
            access_token=access_token,
            refresh_token=refresh_token,
            roles=roles
        )
    except IntegrityError:
        logger.warning(f"Duplicate email or username: {user_data.email}, {user_data.username}")
        raise HTTPException(status_code=409, detail=ErrorMessages.CONFLICT)
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def login_user(login_data: UserLogin) -> UserResponse:
    try:
        user = await User.get_or_none(email=login_data.email).prefetch_related("user_roles__role")
        if not user:
            logger.warning(f"Login failed: User not found for email: {login_data.email}")
            raise HTTPException(status_code=401, detail=ErrorMessages.UNAUTHORIZED)

        if not verify_password(login_data.password, user.passwordHash):
            logger.warning(f"Login failed: Invalid password for email: {login_data.email}")
            raise HTTPException(status_code=401, detail=ErrorMessages.UNAUTHORIZED)

        # Generate access token
        access_token = create_access_token({"sub": str(user.id)})

        # Generate and store refresh token
        refresh_token = create_refresh_token({"sub": str(user.id)})
        await RefreshToken.create(
            user=user,
            token=refresh_token,
            expiresAt=datetime.now(timezone.utc) + timedelta(days=7),
            revoked=datetime.now(timezone.utc) + timedelta(days=30),
            status="active"
        )
        logger.info(f"User logged in: {user.email}")

        # Fetch roles for response
        user_roles = await user.user_roles.all().prefetch_related("role")
        roles = [
            RoleResponse(
                id=ur.role.id,
                name=ur.role.name,
                description=ur.role.description,
                status=ur.role.status
            ) for ur in user_roles
        ]

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            status=user.status,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt,
            access_token=access_token,
            refresh_token=refresh_token,
            roles=roles
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def get_all_users() -> list[UserResponse]:
    try:
        users = await User.all().prefetch_related("user_roles__role")
        logger.info(f"Fetched {len(users)} users")
        user_responses = []
        for user in users:
            roles = [
                RoleResponse(
                    id=ur.role.id,
                    name=ur.role.name,
                    description=ur.role.description,
                    status=ur.role.status
                ) for ur in user.user_roles
            ]
            user_responses.append(
                UserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    status=user.status,
                    createdAt=user.createdAt,
                    updatedAt=user.updatedAt,
                    access_token="",
                    refresh_token="",
                    roles=roles
                )
            )
        return user_responses
    except Exception as e:
        logger.error(f"Error fetching users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def get_user_by_id(user_id: str) -> UserResponse:
    try:
        user = await User.get_or_none(id=user_id).prefetch_related("user_roles__role")
        if not user:
            logger.warning(f"User not found for id: {user_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND)

        roles = [
            RoleResponse(
                id=ur.role.id,
                name=ur.role.name,
                description=ur.role.description,
                status=ur.role.status
            ) for ur in user.user_roles
        ]

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            status=user.status,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt,
            access_token="",
            refresh_token="",
            roles=roles
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def update_user(user_id: str, user_data: UserUpdate) -> UserResponse:
    try:
        user = await User.get_or_none(id=user_id)
        if not user:
            logger.warning(f"User not found for id: {user_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND)

        # Update user fields
        update_dict = user_data.dict(exclude_unset=True, exclude={"roles"})
        if "password" in update_dict:
            update_dict["passwordHash"] = get_password_hash(update_dict.pop("password"))
        if update_dict:
            await user.update_from_dict(update_dict).save()
            logger.info(f"Updated user fields for {user.email}: {update_dict.keys()}")

        # Add new roles if provided
        if user_data.roles:
            for role_name in set(user_data.roles):  # Avoid duplicates
                role = await Role.get_or_none(name=role_name)
                if not role:
                    logger.warning(f"Role not found: {role_name}")
                    raise HTTPException(status_code=400, detail=ErrorMessages.NOT_FOUND)
                # Check if user already has this role
                existing = await UserRole.filter(user_id=user.id, role_id=role.id).exists()
                if not existing:
                    await UserRole.create(
                        user=user,
                        role=role,
                        description=f"Assigned role {role_name}",
                        status="active"
                    )
                    logger.info(f"Assigned role '{role_name}' to user: {user.email}")
                else:
                    logger.debug(f"User {user.email} already has role: {role_name}")

        # Fetch updated roles for response
        user_roles = await user.user_roles.all().prefetch_related("role")
        roles = [
            RoleResponse(
                id=ur.role.id,
                name=ur.role.name,
                description=ur.role.description,
                status=ur.role.status
            ) for ur in user_roles
        ]

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            status=user.status,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt,
            access_token="",
            refresh_token="",
            roles=roles
        )
    except IntegrityError:
        logger.warning(f"Duplicate email or username during update: {user_data.email}, {user_data.username}")
        raise HTTPException(status_code=409, detail=ErrorMessages.CONFLICT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def refresh_token(refresh_data: RefreshRequest) -> UserResponse:
    try:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Invalid refresh token: missing user_id")
            raise HTTPException(status_code=401, detail=ErrorMessages.INVALID_TOKEN)

        # Verify refresh token exists and is valid
        refresh_token = await RefreshToken.get_or_none(
            token=refresh_data.refresh_token,
            user_id=user_id,
            status="active",
            expiresAt__gte=datetime.now(timezone.utc)
        )
        if not refresh_token:
            logger.warning(f"Refresh token not found or expired for user_id: {user_id}")
            raise HTTPException(status_code=401, detail=ErrorMessages.INVALID_TOKEN)

        # Fetch user
        user = await User.get_or_none(id=user_id).prefetch_related("user_roles__role")
        if not user:
            logger.warning(f"User not found for id: {user_id}")
            raise HTTPException(status_code=401, detail=ErrorMessages.INVALID_TOKEN)

        # Generate new access token
        new_access_token = create_access_token({"sub": str(user.id)})

        # Generate new refresh token
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        await RefreshToken.create(
            user=user,
            token=new_refresh_token,
            expiresAt=datetime.now(timezone.utc) + timedelta(days=7),
            revoked=datetime.now(timezone.utc) + timedelta(days=30),
            status="active"
        )

        # Revoke old refresh token
        refresh_token.status = "revoked"
        refresh_token.revoked = datetime.now(timezone.utc)
        await refresh_token.save()
        logger.info(f"Refreshed tokens for user: {user.email}")

        # Fetch roles for response
        user_roles = await user.user_roles.all().prefetch_related("role")
        roles = [
            RoleResponse(
                id=ur.role.id,
                name=ur.role.name,
                description=ur.role.description,
                status=ur.role.status
            ) for ur in user_roles
        ]

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            status=user.status,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            roles=roles
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail=ErrorMessages.INVALID_TOKEN)

async def revoke_token(refresh_token: str) -> None:
    try:
        token = await RefreshToken.get_or_none(token=refresh_token, status="active")
        if not token:
            logger.warning("Refresh token not found or already revoked")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_TOKEN)

        token.status = "revoked"
        token.revoked = datetime.now(timezone.utc)
        await token.save()
        logger.info(f"Revoked refresh token for user_id: {token.user_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)