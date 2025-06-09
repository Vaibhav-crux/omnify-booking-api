from fastapi import APIRouter, HTTPException
from app.schemas.user import RefreshRequest, UserResponse
from app.services.user import refresh_token, revoke_token
import logging

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger("devanchor.routes.auth")

@router.post("/refresh", response_model=UserResponse)
async def refresh_access_token(refresh_data: RefreshRequest):
    logger.info("POST request to refresh token")
    return await refresh_token(refresh_data)

@router.post("/revoke", status_code=204)
async def revoke_refresh_token(refresh_data: RefreshRequest):
    logger.info("POST request to revoke token")
    await revoke_token(refresh_data.refresh_token)
    return None