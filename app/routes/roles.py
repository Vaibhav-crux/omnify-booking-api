from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.roles import RoleCreate, RoleUpdate, RoleResponse
from app.services.roles import create_role, get_all_roles, update_role, delete_role
import logging

router = APIRouter(prefix="/roles", tags=["Roles"])
logger = logging.getLogger("devanchor.routes.roles")

@router.post("", response_model=RoleResponse, status_code=201)
async def create_new_role(role: RoleCreate):
    logger.info(f"POST request to create role: {role.name}")
    return await create_role(role)

@router.get("", response_model=List[RoleResponse])
async def list_roles(status: str = None):
    logger.info(f"GET request for roles with status filter: {status}")
    return await get_all_roles(status)

@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role_details(role_id: str, role_data: RoleUpdate):
    logger.info(f"PATCH request to update role: {role_id}")
    return await update_role(role_id, role_data)

@router.delete("/{role_id}", status_code=204)
async def delete_role_by_id(role_id: str):
    logger.info(f"DELETE request for role: {role_id}")
    await delete_role(role_id)
    return None