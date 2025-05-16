from datetime import datetime
from enum import Enum

import uuid6
from pytz import timezone
from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.config import settings

from . import Base


class MapsetStatus(str, Enum):
    approved = "approved"
    rejected = "rejected"
    on_verification = "on_verification"


class MapsetModel(Base):
    __tablename__ = "mapsets"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scale = Column(String(29), nullable=False)
    layer_url = Column(Text)
    metadata_url = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    classification_id = Column(UUID(as_uuid=True), ForeignKey("classifications.id"))
    regional_id = Column(UUID(as_uuid=True), ForeignKey("regionals.id"), nullable=True)
    projection_system_id = Column(UUID(as_uuid=True), ForeignKey("map_projection_systems.id"))
    producer_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    status_validation = Column(String(20), nullable=True)
    data_status = Column(String(20), nullable=False)
    data_update_period = Column(String(20), nullable=False)
    data_version = Column(String(20), nullable=False)
    coverage_level = Column(String(20), nullable=True)
    coverage_area = Column(String(20), nullable=True)
    is_popular = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)))
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    projection_system = relationship("MapProjectionSystemModel", uselist=False, lazy="selectin")
    classification = relationship("ClassificationModel", uselist=False, lazy="selectin")
    category = relationship("CategoryModel", uselist=False, lazy="selectin")
    regional = relationship("RegionalModel", uselist=False, lazy="selectin")
    source_usages = relationship("SourceUsageModel", back_populates="mapset", lazy="selectin")
    sources = relationship(
        "MapSourceModel",
        secondary="source_usages",
        primaryjoin="MapsetModel.id == SourceUsageModel.mapset_id",
        secondaryjoin="SourceUsageModel.source_id == MapSourceModel.id",
        lazy="selectin",
        viewonly=True,
    )
    producer = relationship("OrganizationModel", back_populates="mapsets", uselist=False, lazy="selectin")
