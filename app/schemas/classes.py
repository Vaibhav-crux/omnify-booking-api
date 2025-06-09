from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List
from app.database.models.enums import RecordStatus
import pendulum
from app.utils.constants import ClassesBooking

class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    schedule: datetime
    slots: int = Field(..., ge=1)

    @validator("schedule")
    def validate_schedule(cls, value):
        if not value.tzinfo:
            raise ValueError("Schedule must be timezone-aware")
        # Convert to pendulum DateTime for timezone validation
        pendulum_dt = pendulum.instance(value)
        # Create a pendulum DateTime in Asia/Kolkata to get its offset
        ist = pendulum.now(ClassesBooking.DEFAULT_TIMEZONE)
        # Check if the offset matches Asia/Kolkata's offset (+05:30)
        if pendulum_dt.utcoffset() != ist.utcoffset():
            raise ValueError(f"Schedule must be in {ClassesBooking.DEFAULT_TIMEZONE} timezone (UTC+05:30)")
        return value

class ClassResponse(BaseModel):
    id: str
    name: str
    date: str
    time: str
    instructor: str
    available_slots: int
    status: str
    timezone: str

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            RecordStatus: lambda v: v.value
        }

class PaginatedClassResponse(BaseModel):
    items: List[ClassResponse]
    total: int
    page: int
    limit: int
    total_pages: int