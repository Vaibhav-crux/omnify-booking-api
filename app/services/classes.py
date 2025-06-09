from app.database.models.classes import Class
from app.database.models.bookings import Booking
from app.database.models.users import User
from app.schemas.classes import ClassCreate, ClassResponse, PaginatedClassResponse
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction
from fastapi import HTTPException
from app.utils.constants import ErrorMessages, ClassesBooking
import logging
from math import ceil
import pendulum

logger = logging.getLogger("devanchor.services.classes")

async def create_class(class_data: ClassCreate, user: User) -> ClassResponse:
    try:
        # Validate schedule is in the future
        ist = pendulum.timezone(ClassesBooking.DEFAULT_TIMEZONE)
        now = pendulum.now(ist)
        if class_data.schedule <= now:
            logger.warning(f"Invalid schedule: {class_data.schedule} is not in the future")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_SCHEDULE)

        # Convert schedule to UTC for storage
        schedule_utc = class_data.schedule.astimezone(pendulum.timezone("UTC"))

        async with in_transaction():
            # Create class with authenticated user as instructor
            class_instance = await Class.create(
                name=class_data.name,
                instructor=user,
                schedule=schedule_utc,
                slots=class_data.slots,
                status="active"
            )
            logger.info(f"Class created: {class_data.name} by instructor {user.username}")

        # Construct response in IST
        schedule_ist = class_instance.schedule.astimezone(ist)
        return ClassResponse(
            id=class_instance.id,
            name=class_instance.name,
            date=schedule_ist.date().isoformat(),
            time=schedule_ist.time().isoformat(),
            instructor=user.username,
            available_slots=class_instance.slots,
            status=class_instance.status,
            timezone=ClassesBooking.DEFAULT_TIMEZONE
        )
    except IntegrityError:
        logger.warning("Error creating class: Duplicate or invalid data")
        raise HTTPException(status_code=409, detail=ErrorMessages.CONFLICT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating class: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def get_all_classes(page: int = 1, limit: int = 10, timezone: str = ClassesBooking.DEFAULT_TIMEZONE) -> PaginatedClassResponse:
    try:
        # Validate pagination parameters
        if page < 1:
            logger.warning(f"Invalid page number: {page}")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_PAGE)
        if limit < 1 or limit > 100:
            logger.warning(f"Invalid limit: {limit}")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_LIMIT)

        # Validate timezone
        try:
            tz = pendulum.timezone(timezone)
        except pendulum.exceptions.InvalidTimezone:
            logger.warning(f"Invalid timezone: {timezone}")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_TIMEZONE)

        # Calculate offset
        offset = (page - 1) * limit

        async with in_transaction():
            # Fetch total count and paginated classes
            total = await Class.all().count()
            classes = await Class.all().prefetch_related("instructor", "bookings").offset(offset).limit(limit)

        if not classes:
            logger.info("No classes found")
            return PaginatedClassResponse(
                items=[],
                total=0,
                page=page,
                limit=limit,
                total_pages=0
            )

        # Construct response
        responses = []
        for class_instance in classes:
            # Calculate available slots
            active_bookings = await Booking.filter(
                class_=class_instance.id,
                status="active"
            ).count()
            available_slots = class_instance.slots - active_bookings

            # Convert schedule to client's timezone
            schedule_tz = class_instance.schedule.astimezone(tz)
            responses.append(
                ClassResponse(
                    id=class_instance.id,
                    name=class_instance.name,
                    date=schedule_tz.date().isoformat(),
                    time=schedule_tz.time().isoformat(),
                    instructor=class_instance.instructor.username,
                    available_slots=available_slots,
                    status=class_instance.status,
                    timezone=timezone
                )
            )

        logger.info(f"Fetched {len(classes)} classes for page {page}, limit {limit}, timezone {timezone}")
        return PaginatedClassResponse(
            items=responses,
            total=total,
            page=page,
            limit=limit,
            total_pages=ceil(total / limit)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching classes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)