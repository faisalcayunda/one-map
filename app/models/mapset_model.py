from datetime import datetime

import uuid6
from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from . import Base


class MapsetModel(Base):
    __tablename__ = "mapsets"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scale = Column(String(29), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    classification_id = Column(UUID(as_uuid=True), ForeignKey("classifications.id"))
    regional_id = Column(UUID(as_uuid=True), ForeignKey("regionals.id"))
    projection_system_id = Column(UUID(as_uuid=True), ForeignKey("map_projection_systems.id"))
    source_id = Column(UUID(as_uuid=True), ForeignKey("map_sources.id"))
    producer_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    data_status = Column(String(20), nullable=False)
    data_update_period = Column(String(20), nullable=False)
    data_version = Column(String(20), nullable=False)
    is_popular = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    projection_system = relationship("MapProjectionSystemModel", uselist=False, lazy="selectin")
    classification = relationship("ClassificationModel", uselist=False, lazy="selectin")
    category = relationship("CategoryModel", uselist=False, lazy="selectin")
    regional = relationship("RegionalModel", uselist=False, lazy="selectin")
    source = relationship("MapSourceModel", uselist=False, lazy="selectin")
    producer = relationship("OrganizationModel", back_populates="mapsets", uselist=False, lazy="selectin")
