from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.database.models.enums import RecordStatus

class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)  # e.g., "Yoga"
    schedule: datetime  # Date and time of the class
    slots: int = Field(..., ge=1)  # Number of available spots

class ClassResponse(BaseModel):
    id: str
    name: str
    date: str  # ISO date, e.g., "2025-06-09"
    time: str  # ISO time, e.g., "10:00:00"
    instructor: str  # Instructor's name (username)
    available_slots: int
    status: str

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