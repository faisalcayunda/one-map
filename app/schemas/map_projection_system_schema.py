from typing import Optional

from pydantic import Field

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel


class MapProjectionSystemSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str


class MapProjectionSystemCreateSchema(ORJSONBaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class MapProjectionSystemUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
