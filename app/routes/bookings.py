from fastapi import APIRouter, Depends
from typing import List
from app.schemas.bookings import BookingCreate, BookingResponse
from app.services.bookings import create_booking, get_user_bookings
from app.middleware.auth import get_current_user
from app.database.models.users import User

router = APIRouter()

@router.post("/book", response_model=BookingResponse, status_code=201)
async def create_booking_endpoint(
    booking_data: BookingCreate,
    user: User = Depends(get_current_user)
):
    return await create_booking(booking_data, user)

@router.get("/bookings", response_model=List[BookingResponse])
async def get_user_bookings_endpoint(user: User = Depends(get_current_user)):
    return await get_user_bookings(user)