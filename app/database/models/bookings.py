from tortoise import fields
from app.database.models.base_model import BaseModel
from app.database.models.enums import RecordStatus
from app.database.models.users import User

class Booking(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="bookings", index=True)
    class_ = fields.ForeignKeyField("models.Class", related_name="bookings", index=True)
    status = fields.CharEnumField(enum_type=RecordStatus, default=RecordStatus.active, index=True)

    class Meta:
        table = "bookings"
        unique_together = (("user", "class_"),)  # Prevent duplicate bookings by the same user for the same class