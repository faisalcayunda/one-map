from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel


class OrganizationSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    description: Optional[str]
    thumbnail: Optional[str]
    address: Optional[str]
    phone_number: Optional[str]
    email: Optional[EmailStr]
    website: Optional[str]
    count_mapset: int
    is_active: bool
    created_at: datetime
    modified_at: Optional[datetime]


class OrganizationCreateSchema(ORJSONBaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    thumbnail: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=1, max_length=15)
    email: Optional[EmailStr] = Field(None, max_length=100)
    website: Optional[str] = Field(None, min_length=1, max_length=100)


class OrganizationUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    thumbnail: Optional[str] = Field(None, min_length=1, max_length=500)
    phone_number: Optional[str] = Field(None, min_length=1, max_length=15)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    email: Optional[EmailStr] = Field(None)
    website: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = Field(None)
    is_deleted: Optional[bool] = Field(None)
