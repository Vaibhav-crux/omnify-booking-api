from tortoise import fields
from app.database.models.base_model import BaseModel
from app.database.models.enums import UserStatus
from .refresh_tokens import RefreshToken
from .user_roles import UserRole

class User(BaseModel):
    email = fields.CharField(max_length=255, unique=True, index=True)
    username = fields.CharField(max_length=255, unique=True, index=True)
    passwordHash = fields.CharField(max_length=255)
    status = fields.CharEnumField(enum_type=UserStatus, default=UserStatus.active, index=True)

    # Relationships
    refresh_tokens = fields.ReverseRelation["RefreshToken"]
    user_roles = fields.ReverseRelation["UserRole"]

    class Meta:
        table = "users"