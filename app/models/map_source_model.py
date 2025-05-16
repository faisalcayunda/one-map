from datetime import datetime

import uuid6
from pytz import timezone
from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.config import settings

from . import Base


class MapSourceModel(Base):
    __tablename__ = "map_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    url = Column(Text, nullable=True)
    credential_id = Column(UUID(as_uuid=True), ForeignKey("credentials.id"))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)))
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )

    usages = relationship("SourceUsageModel", back_populates="source", lazy="selectin")
    mapsets = relationship(
        "MapsetModel",
        secondary="source_usages",
        primaryjoin="MapSourceModel.id == SourceUsageModel.source_id",
        secondaryjoin="SourceUsageModel.mapset_id == MapsetModel.id",
        lazy="selectin",
        viewonly=True,
    )
    credential = relationship("CredentialModel", lazy="selectin", uselist=False)


class SourceUsageModel(Base):
    __tablename__ = "source_usages"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    source_id = Column(UUID(as_uuid=True), ForeignKey("map_sources.id"), nullable=False)
    mapset_id = Column(UUID(as_uuid=True), ForeignKey("mapsets.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)))
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )

    mapset = relationship("MapsetModel", back_populates="source_usages")
    source = relationship("MapSourceModel", back_populates="usages")
