from datetime import datetime

import uuid6
from pytz import timezone
from sqlalchemy import UUID, Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.core.config import settings

from . import Base


class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)))
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )

    users = relationship("UserModel", lazy="selectin")

    # Relationships
    # organization = relationship("OrganizationModel", back_populates="members")
    # produced_mapsets = relationship("MapsetModel", back_populates="producer")
    # mapset_access = relationship("MapsetAccessModel", foreign_keys=[MapsetAccessModel.user_id], back_populates="user")
