from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.bookings import BookingCreate, BookingResponse
from app.services.bookings import create_booking, get_user_bookings
from app.middleware.auth import get_current_user
from app.database.models.users import User

router = APIRouter()

@router.post("/book", response_model=BookingResponse, status_code=201)
async def create_booking_endpoint(
    booking_data: BookingCreate,
    timezone: str = Query("Asia/Kolkata", description="Client timezone (e.g., America/New_York)"),
    user: User = Depends(get_current_user)
):
    return await create_booking(booking_data, user, timezone=timezone)

@router.get("/bookings", response_model=List[BookingResponse])
async def get_user_bookings_endpoint(
    timezone: str = Query("Asia/Kolkata", description="Client timezone (e.g., America/New_York)"),
    user: User = Depends(get_current_user)
):
    return await get_user_bookings(user, timezone=timezone)