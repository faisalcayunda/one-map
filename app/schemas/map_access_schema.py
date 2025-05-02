from typing import Optional

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel


class MapAccessSchema(ORJSONBaseModel):
    id: UUID7Field
    mapset_id: UUID7Field
    user_id: Optional[UUID7Field] = None
    organization_id: Optional[UUID7Field] = None
    can_read: bool
    can_write: bool
    can_delete: bool


class MapAccessCreateSchema(ORJSONBaseModel):
    mapset_id: UUID7Field
    user_id: Optional[UUID7Field] = None
    organization_id: Optional[UUID7Field] = None
    can_read: bool
    can_write: bool
    can_delete: bool


class MapAccessUpdateSchema(ORJSONBaseModel):
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None
    can_delete: Optional[bool] = None
