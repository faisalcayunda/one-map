from datetime import datetime
from typing import Optional

from pytz import timezone
from sqlalchemy import UUID as SQLUUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped
from uuid6 import UUID, uuid7

from app.core.config import settings

from . import Base


class MapAccessModel(Base):
    __tablename__ = "mapset_access"

    id: Mapped[UUID] = Column(String, primary_key=True, default=uuid7)
    mapset_id: Mapped[UUID] = Column(
        SQLUUID(as_uuid=True), ForeignKey("mapsets.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[UUID]] = Column(
        SQLUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    organization_id: Mapped[Optional[UUID]] = Column(
        SQLUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    granted_by: Mapped[UUID] = Column(SQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    can_read: Mapped[bool] = Column(Boolean, default=True)
    can_write: Mapped[bool] = Column(Boolean, default=False)
    can_delete: Mapped[bool] = Column(Boolean, default=False)

    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )
    # expires_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)  # Optional expiry

    # Relationships
    # mapset = relationship("MapsetModel", back_populates="access_grants")
    # user = relationship("UserModel", foreign_keys=[user_id], back_populates="mapset_access")
    # organization = relationship("OrganizationModel", back_populates="mapset_access")
    # grantor = relationship("UserModel", foreign_keys=[granted_by])
