from datetime import datetime
from typing import Optional

from pydantic import Field

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel
from app.schemas import CredentialSchema


class MapSourceSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    description: Optional[str]
    credential: CredentialSchema
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime]


class MapSourceCreateSchema(ORJSONBaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None)
    credential_id: UUID7Field
    is_active: bool = True


class MapSourceUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None)
    credential_id: Optional[UUID7Field]
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None
