from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from app.database.models.enums import RecordStatus

class BookingCreate(BaseModel):
    class_id: str = Field(..., min_length=1)
    client_name: str = Field(..., min_length=1, max_length=255)
    client_email: EmailStr

class BookingResponse(BaseModel):
    id: str
    class_id: str
    class_name: str
    class_date: str
    class_time: str
    client_name: str
    client_email: str
    status: str
    timezone: str

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            RecordStatus: lambda v: v.value
        }