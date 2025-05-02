from typing import Optional

from pydantic import Field

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel


class ClassificationSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    is_open: bool
    is_limited: bool
    is_secret: bool


class ClassificationCreateSchema(ORJSONBaseModel):
    name: str
    is_open: bool
    is_limited: bool
    is_secret: bool


class ClassificationUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None)
    is_open: Optional[bool] = Field(None)
    is_limited: Optional[bool] = Field(None)
    is_secret: Optional[bool] = Field(None)
