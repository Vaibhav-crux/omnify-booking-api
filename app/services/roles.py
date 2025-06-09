from tortoise.exceptions import IntegrityError
from fastapi import HTTPException
from typing import List, Optional
from app.database.models.roles import Role
from app.schemas.roles import RoleCreate, RoleUpdate, RoleResponse
from app.utils.constants import ErrorMessages, RoleConstants
import logging

logger = logging.getLogger("devanchor.services.roles")

async def create_role(role_data: RoleCreate) -> Role:
    try:
        logger.debug(f"Creating role with name: {role_data.name}")
        role = await Role.create(
            name=role_data.name,  # Already lowercase from schema
            description=role_data.description,
            status=RoleConstants.DEFAULT_STATUS
        )
        logger.info(f"Role created successfully: {role.name}", extra={"role_id": role.id})
        return role
    except IntegrityError:
        logger.error(f"Duplicate role name: {role_data.name}")
        raise HTTPException(status_code=409, detail=RoleConstants.DUPLICATE_NAME)
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def get_all_roles(status: str = None) -> list[Role]:
    try:
        logger.debug(f"Fetching roles with status filter: {status}")
        query = Role.all()
        if status:
            query = query.filter(status=status)
        roles = await query
        logger.info(f"Fetched {len(roles)} roles")
        return roles
    except Exception as e:
        logger.error(f"Error fetching roles: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def update_role(role_id: str, role_data: RoleUpdate) -> Role:
    try:
        role = await Role.get_or_none(id=role_id)
        if not role:
            logger.warning(f"Role not found: {role_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND)

        # Update role fields if provided
        update_dict = role_data.dict(exclude_unset=True)
        if update_dict:
            await role.update_from_dict(update_dict).save()
            logger.info(f"Updated role: {role.name}", extra={"role_id": role.id, "updated_fields": list(update_dict.keys())})
        else:
            logger.debug(f"No updates provided for role: {role_id}")

        return role
    except IntegrityError:
        logger.warning(f"Duplicate role name during update: {role_data.name}")
        raise HTTPException(status_code=409, detail=RoleConstants.DUPLICATE_NAME)
    except Exception as e:
        logger.error(f"Error updating role {role_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def delete_role(role_id: str) -> None:
    try:
        role = await Role.get_or_none(id=role_id)
        if not role:
            logger.warning(f"Role not found: {role_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND)

        await role.delete()
        logger.info(f"Deleted role: {role.name}", extra={"role_id": role.id})
    except Exception as e:
        logger.error(f"Error deleting role {role_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)