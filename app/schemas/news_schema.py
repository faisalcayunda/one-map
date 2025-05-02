from typing import Optional

from pydantic import Field

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel


class NewsSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_active: bool = True


class NewsCreateSchema(ORJSONBaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_active: bool = True


class NewsUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_active: Optional[bool] = None
