from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.core.data_types import UUID7Field
from app.core.serializers import ORJSONBaseModel
from app.schemas.category_schema import CategorySchema
from app.schemas.classification_schema import ClassificationSchema
from app.schemas.map_projection_system_schema import MapProjectionSystemSchema
from app.schemas.map_source_schema import MapSourceSchema
from app.schemas.organization_schema import OrganizationWithMapsetSchema
from app.schemas.regional_schema import RegionalSchema


class MapsetSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    description: str
    scale: Optional[str]
    layer_url: Optional[str]
    metadata_url: Optional[str]
    status_validation: Optional[str]
    classification: str
    data_status: str
    data_update_period: Optional[str]
    data_version: Optional[str]
    coverage_level: Optional[str]
    coverage_area: Optional[str]
    category: CategorySchema
    projection_system: MapProjectionSystemSchema
    producer: OrganizationWithMapsetSchema
    regional: RegionalSchema
    source: MapSourceSchema
    classification: ClassificationSchema
    is_popular: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MapsetByOrganizationSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    found: int
    mapsets: List[MapsetSchema]


class MapsetCreateSchema(ORJSONBaseModel):
    name: str
    description: Optional[str] = Field(None)
    scale: Optional[str] = Field(None)
    layer_url: str
    metadata_url: Optional[str] = Field(None)
    status_validation: str
    projection_system_id: UUID7Field
    category_id: UUID7Field
    classification_id: UUID7Field
    source_id: UUID7Field
    regional_id: UUID7Field
    producer_id: UUID7Field
    data_status: str
    data_update_period: Optional[str] = Field(default=None)
    data_version: Optional[str] = Field(default=None)
    coverage_level: Optional[str] = Field(default=None)
    coverage_area: Optional[str] = Field(default=None)
    is_popular: bool = Field(default=False)
    is_active: bool = Field(default=True)


class MapsetUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    scale: Optional[str] = Field(None)
    layer_url: Optional[str] = Field(None)
    metadata_url: Optional[str] = Field(None)
    status_validation: Optional[str] = Field(None)
    projection_system_id: Optional[UUID7Field] = Field(None)
    category_id: Optional[UUID7Field] = Field(None)
    classification_id: Optional[UUID7Field] = Field(None)
    source_id: Optional[UUID7Field] = Field(None)
    regional_id: Optional[UUID7Field] = Field(None)
    producer_id: Optional[UUID7Field] = Field(None)
    data_status: Optional[str] = Field(None)
    data_update_period: Optional[str] = Field(None)
    data_version: Optional[str] = Field(None)
    coverage_level: Optional[str] = Field(None)
    coverage_area: Optional[str] = Field(None)
    is_popular: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)
