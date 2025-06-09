from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.utils.constants import RoleConstants
from app.database.models.enums import RecordStatus

class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=RoleConstants.MAX_NAME_LENGTH)
    description: Optional[str] = None

    @validator("name")
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError(RoleConstants.NAME_REQUIRED)
        return value.strip().lower()

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=RoleConstants.MAX_NAME_LENGTH)
    description: Optional[str] = None
    status: Optional[RecordStatus] = None

    @validator("name")
    def validate_name(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError(RoleConstants.NAME_REQUIRED)
        return value.strip().lower()

    class Config:
        extra = "forbid"

class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: RecordStatus
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            RecordStatus: lambda v: v.value
        }