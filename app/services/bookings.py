from app.database.models.bookings import Booking
from app.database.models.classes import Class
from app.database.models.users import User
from app.schemas.bookings import BookingCreate, BookingResponse
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction
from fastapi import HTTPException
from app.utils.constants import ErrorMessages, ClassesBooking
import logging
import pendulum

logger = logging.getLogger("devanchor.services.bookings")

async def create_booking(booking_data: BookingCreate, user: User, timezone: str = ClassesBooking.DEFAULT_TIMEZONE) -> BookingResponse:
    try:
        # Validate timezone
        try:
            tz = pendulum.timezone(timezone)
        except pendulum.exceptions.InvalidTimezone:
            logger.warning(f"Invalid timezone: {timezone}")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_TIMEZONE)

        async with in_transaction():
            # Validate class
            class_instance = await Class.get_or_none(id=booking_data.class_id)
            if not class_instance or class_instance.status != "active":
                logger.warning(f"Class not found or inactive: {booking_data.class_id}")
                raise HTTPException(status_code=404, detail=ErrorMessages.NOT_FOUND)

            # Check booking deadline (30 minutes before class start)
            ist = pendulum.timezone(ClassesBooking.DEFAULT_TIMEZONE)
            class_start = class_instance.schedule.astimezone(ist)
            now = pendulum.now(ist)
            if class_start <= now.add(minutes=30):
                logger.warning(f"Booking deadline passed for class: {booking_data.class_id}")
                raise HTTPException(status_code=400, detail=ErrorMessages.BOOKING_DEADLINE_PASSED)

            # Check available slots
            active_bookings = await Booking.filter(class_=class_instance, status="active").count()
            if active_bookings >= class_instance.slots:
                logger.warning(f"No slots available for class: {booking_data.class_id}")
                raise HTTPException(status_code=400, detail="No slots available for this class.")

            # Validate client email matches authenticated user
            if booking_data.client_email != user.email:
                logger.warning(f"Email mismatch: {booking_data.client_email} != {user.email}")
                raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_REQUEST)

            # Create booking
            booking = await Booking.create(
                user=user,
                class_=class_instance,
                status="active"
            )
            logger.info(f"Booking created for class {booking_data.class_id} by user {user.email}")

        # Construct response in client's timezone
        schedule_tz = class_instance.schedule.astimezone(tz)
        return BookingResponse(
            id=booking.id,
            class_id=class_instance.id,
            class_name=class_instance.name,
            class_date=schedule_tz.date().isoformat(),
            class_time=schedule_tz.time().isoformat(),
            client_name=booking_data.client_name,
            client_email=booking_data.client_email,
            status=booking.status,
            timezone=timezone
        )
    except IntegrityError:
        logger.warning(f"Duplicate booking for class {booking_data.class_id} by user {user.email}")
        raise HTTPException(status_code=409, detail=ErrorMessages.CONFLICT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating booking: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def get_user_bookings(user: User, timezone: str = ClassesBooking.DEFAULT_TIMEZONE) -> list[BookingResponse]:
    try:
        # Validate timezone
        try:
            tz = pendulum.timezone(timezone)
        except pendulum.exceptions.InvalidTimezone:
            logger.warning(f"Invalid timezone: {timezone}")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_TIMEZONE)

        async with in_transaction():
            bookings = await Booking.filter(user=user, status="active").prefetch_related("class_")

        if not bookings:
            logger.info(f"No bookings found for user: {user.email}")
            return []

        responses = [
            BookingResponse(
                id=booking.id,
                class_id=booking.class_.id,
                class_name=booking.class_.name,
                class_date=booking.class_.schedule.astimezone(tz).date().isoformat(),
                class_time=booking.class_.schedule.astimezone(tz).time().isoformat(),
                client_name=user.username,
                client_email=user.email,
                status=booking.status,
                timezone=timezone
            )
            for booking in bookings
        ]
        logger.info(f"Fetched {len(bookings)} bookings for user: {user.email}")
        return responses
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bookings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)