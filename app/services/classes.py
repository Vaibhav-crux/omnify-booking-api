from app.database.models.classes import Class
from app.database.models.bookings import Booking
from app.database.models.users import User
from app.schemas.classes import ClassCreate, ClassResponse, PaginatedClassResponse
from tortoise.exceptions import IntegrityError
from fastapi import HTTPException
from app.utils.constants import ErrorMessages
import logging
from math import ceil

logger = logging.getLogger("devanchor.services.classes")

async def create_class(class_data: ClassCreate, user: User) -> ClassResponse:
    try:
        # Create class with authenticated user as instructor
        class_instance = await Class.create(
            name=class_data.name,
            instructor=user,
            schedule=class_data.schedule,
            slots=class_data.slots,
            status="active"
        )
        logger.info(f"Class created: {class_data.name} by instructor {user.username}")

        # Construct response
        return ClassResponse(
            id=class_instance.id,
            name=class_instance.name,
            date=class_instance.schedule.date().isoformat(),
            time=class_instance.schedule.time().isoformat(),
            instructor=user.username,  # Use username instead of email
            available_slots=class_instance.slots,
            status=class_instance.status
        )
    except IntegrityError:
        logger.warning("Error creating class: Duplicate or invalid data")
        raise HTTPException(status_code=409, detail=ErrorMessages.CONFLICT)
    except Exception as e:
        logger.error(f"Error creating class: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR)

async def get_all_classes(page: int = 1, limit: int = 10) -> PaginatedClassResponse:
    try:
        # Validate pagination parameters
        if page < 1:
            logger.warning(f"Invalid page number: {page}")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_PAGE)
        if limit < 1 or limit > 100:
            logger.warning(f"Invalid limit: {limit}")
            raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_LIMIT)

        # Calculate offset
        offset = (page - 1) * limit

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
                class_=class_instance, status="active"
            ).count()
            available_slots = class_instance.slots - active_bookings

            responses.append(
                ClassResponse(
                    id=class_instance.id,
                    name=class_instance.name,
                    date=class_instance.schedule.date().isoformat(),
                    time=class_instance.schedule.time().isoformat(),
                    instructor=class_instance.instructor.username,  # Use username instead of email
                    available_slots=available_slots,
                    status=class_instance.status
                )
            )

        logger.info(f"Fetched {len(classes)} classes for page {page}, limit {limit}")
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