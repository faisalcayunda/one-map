from typing import Optional

from pydantic import Field

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel


class RegionalSchema(ORJSONBaseModel):
    id: UUID7Field
    code: str
    name: str
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_active: bool = True


class RegionalCreateSchema(ORJSONBaseModel):
    code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_active: bool = True


class RegionalUpdateSchema(ORJSONBaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    is_active: Optional[bool] = None
