from fastapi import HTTPException
from typing import List
from app.utils.constants import ErrorMessages
import re
import logging

logger = logging.getLogger("devanchor.auth.permissions")

# Define permissions: {path: {method: allowed_roles}}
# '*' means all roles are allowed
PERMISSIONS = {
    "/api/v1/users": {
        "GET": ["admin"],  
        "POST": ["*"],                  
    },
    "/api/v1/users/login": {
        "POST": ["*"],                  
    },
    "/api/v1/users/{user_id}": {
        "GET": ["*"],                   
        "PATCH": ["*"],                 
        "DELETE": ["admin"],            
    },
    "/api/v1/users/me": {
        "GET": ["*"],                   
        "PATCH": ["*"],                 
    },
    "/api/v1/roles": {
        "GET": ["*"],                   
        "POST": ["*"],                  
    },
    "/api/v1/roles/": {
        "GET": ["*"],                   
        "POST": ["*"],                  
    },
    "/api/v1/roles/{role_id}": {
        "PATCH": ["admin"], 
        "DELETE": ["admin"],
    },
    "/api/v1/auth/refresh": {
        "POST": ["*"],                  
    },
    "/api/v1/auth/revoke": {
        "POST": ["*"],                  
    },
    "/api/v1/health": {
        "GET": ["*"],                  
    },
    "/api/v1/classes": {
        "GET": ["*"],                   
        "POST": ["*"],                  
    },
    "/api/v1/book": {
        "POST": ["*"],  
    },
    "/api/v1/bookings": {
        "GET": ["*"], 
    },
}

def normalize_path(path: str) -> str:
    uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    normalized = re.sub(uuid_pattern, "{user_id}", path)
    normalized = normalized.replace("{user_id}", "{role_id}", 1) if "/roles/" in path else normalized
    return normalized

async def check_permissions(path: str, method: str, user_roles: List[str]) -> None:

    normalized_path = normalize_path(path)
    logger.debug(f"Checking permissions for {method} {normalized_path} with roles: {user_roles}")

    path_permissions = PERMISSIONS.get(normalized_path)
    if not path_permissions:
        logger.warning(f"No permissions defined for path: {normalized_path}")
        raise HTTPException(status_code=403, detail=ErrorMessages.FORBIDDEN)

    allowed_roles = path_permissions.get(method)
    if not allowed_roles:
        logger.warning(f"No permissions defined for method {method} on path: {normalized_path}")
        raise HTTPException(status_code=403, detail=ErrorMessages.FORBIDDEN)

    if "*" in allowed_roles:
        logger.debug(f"Access granted for {method} {normalized_path} (all roles allowed)")
        return

    if not any(role in allowed_roles for role in user_roles):
        logger.warning(f"Access denied for user with roles {user_roles} to {method} {normalized_path}")
        raise HTTPException(status_code=403, detail=ErrorMessages.FORBIDDEN)

    logger.debug(f"Access granted for user with roles {user_roles} to {method} {normalized_path}")