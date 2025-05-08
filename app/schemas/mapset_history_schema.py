from datetime import datetime
from typing import Optional

from pydantic import Field

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel
from app.schemas.user_schema import UserSchema


class MapsetHistorySchema(ORJSONBaseModel):
    id: UUID7Field
    mapset_id: UUID7Field
    validation_type: str
    notes: Optional[str]
    timestamp: datetime
    user_info: UserSchema = Field(alias="user")


class MapsetHistoryCreateSchema(ORJSONBaseModel):
    mapset_id: UUID7Field
    validation_type: str = Field(..., min_length=1)
    notes: Optional[str] = None
