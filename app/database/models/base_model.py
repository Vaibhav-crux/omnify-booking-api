from tortoise.models import Model
from tortoise import fields
import uuid

class BaseModel(Model):
    id = fields.CharField(max_length=36, primary_key=True, default=lambda: str(uuid.uuid4()))
    createdAt = fields.DatetimeField(auto_now_add=True)
    updatedAt = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True