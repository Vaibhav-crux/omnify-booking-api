from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.database.models.enums import UserStatus, RecordStatus

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=1)
    status: Optional[UserStatus] = None
    roles: Optional[List[str]] = None  # List of role names to add

    class Config:
        extra = "forbid"  # Prevent unknown fields

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: RecordStatus

    class Config:
        from_attributes = True
        json_encoders = {
            RecordStatus: lambda v: v.value
        }

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    status: UserStatus
    createdAt: datetime
    updatedAt: datetime
    access_token: str
    refresh_token: str
    roles: List[RoleResponse]

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UserStatus: lambda v: v.value
        }