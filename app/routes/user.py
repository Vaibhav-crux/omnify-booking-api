from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserResponse
from app.services.user import create_user, login_user, get_all_users, get_user_by_id, update_user
from app.database.models.users import User
from app.utils.constants import ErrorMessages
import logging

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger("devanchor.routes.users")

async def get_authenticated_user(request: Request) -> User:
    user = request.state.user
    if not user:
        logger.warning("No authenticated user in request state")
        raise HTTPException(status_code=401, detail=ErrorMessages.UNAUTHORIZED)
    return user

@router.post("", response_model=UserResponse, status_code=201)
async def create_new_user(user: UserCreate):
    logger.info(f"POST request to create user: {user.email}")
    return await create_user(user)

@router.post("/login", response_model=UserResponse, status_code=200)
async def login(login_data: UserLogin):
    logger.info(f"POST request to login user: {login_data.email}")
    return await login_user(login_data)

@router.get("", response_model=List[UserResponse])
async def list_users():
    logger.info("GET request for all users")
    return await get_all_users()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    logger.info(f"GET request for user: {user_id}")
    return await get_user_by_id(user_id)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user_details(user_id: str, user_data: UserUpdate):
    logger.info(f"PATCH request to update user: {user_id}")
    return await update_user(user_id, user_data)