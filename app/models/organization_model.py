from datetime import datetime

import uuid6
from pytz import timezone
from sqlalchemy import UUID, Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.core.config import settings

from . import Base


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(15), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, server_default="true")
    is_deleted = Column(Boolean, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone(settings.TIMEZONE)))
    modified_at = Column(
        DateTime(timezone=True),
        nullable=True,
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )

    users = relationship("UserModel", lazy="selectin")
    mapsets = relationship("MapsetModel", lazy="selectin")

    # @property
    # def count_mapset(self):
    #     if self.mapsets is None:
    #         return 0
    #     else:
    #         return len(self.mapsets)
