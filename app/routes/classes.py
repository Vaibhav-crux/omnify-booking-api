from fastapi import APIRouter, Depends, Query
from app.schemas.classes import ClassCreate, ClassResponse, PaginatedClassResponse
from app.services.classes import create_class, get_all_classes
from app.middleware.auth import get_current_user
from app.database.models.users import User

router = APIRouter()

@router.post("/classes", response_model=ClassResponse, status_code=201)
async def create_class_endpoint(
    class_data: ClassCreate,
    user: User = Depends(get_current_user)
):
    return await create_class(class_data, user)

@router.get("/classes", response_model=PaginatedClassResponse)
async def get_all_classes_endpoint(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    timezone: str = Query("Asia/Kolkata", description="Client timezone (e.g., America/New_York)"),
    user: User = Depends(get_current_user)
):
    return await get_all_classes(page=page, limit=limit, timezone=timezone)