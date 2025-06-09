from tortoise import fields
from app.database.models.base_model import BaseModel
from app.database.models.enums import RecordStatus
from app.database.models.users import User

class Class(BaseModel):
    name = fields.CharField(max_length=255, index=True)  # e.g., "Yoga", "Zumba", "HIIT"
    instructor = fields.ForeignKeyField("models.User", related_name="classes_taught", index=True)
    schedule = fields.DatetimeField(index=True)  # Date and time of the class
    slots = fields.IntField(default=10, constraints={"ge": 1})  # Maximum number of spots
    status = fields.CharEnumField(enum_type=RecordStatus, default=RecordStatus.active, index=True)

    # Relationships
    bookings = fields.ReverseRelation["models.Booking"]

    class Meta:
        table = "classes"