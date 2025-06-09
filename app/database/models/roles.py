from tortoise import fields
from app.database.models.base_model import BaseModel
from app.database.models.enums import RecordStatus
from .user_roles import UserRole

class Role(BaseModel):
    name = fields.CharField(max_length=255, unique=True, index=True)
    description = fields.TextField(null=True)
    status = fields.CharEnumField(enum_type=RecordStatus, default=RecordStatus.active)

    # Relationship to user roles
    user_roles = fields.ReverseRelation["UserRole"]

    class Meta:
        table = "roles"