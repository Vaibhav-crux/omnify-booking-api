from tortoise import fields
from app.database.models.base_model import BaseModel
from app.database.models.enums import RecordStatus

class RefreshToken(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="refresh_tokens", index=True)
    token = fields.CharField(max_length=255, unique=True)
    expiresAt = fields.DatetimeField()
    revoked = fields.DatetimeField()
    status = fields.CharEnumField(enum_type=RecordStatus, default=RecordStatus.active)

    class Meta:
        table = "refresh_tokens"
        indexes = ["user_id"]