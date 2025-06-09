from tortoise import fields
from app.database.models.base_model import BaseModel
from app.database.models.enums import RecordStatus

class UserRole(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="user_roles", index=True)
    role = fields.ForeignKeyField("models.Role", related_name="user_roles", index=True)
    description = fields.TextField(null=True)
    status = fields.CharEnumField(enum_type=RecordStatus, default=RecordStatus.active)

    class Meta:
        table = "user_roles"
        indexes = ["user_id", "role_id"]
        unique_together = ("user_id", "role_id")