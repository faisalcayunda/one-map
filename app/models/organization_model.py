from datetime import datetime

import uuid6
from sqlalchemy import UUID, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

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
    count_mapset = Column(Integer, default=0, server_default="0")
    is_active = Column(Boolean, default=True, server_default="true")
    is_deleted = Column(Boolean, default=False, server_default="false")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    modified_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    users = relationship("UserModel", lazy="selectin")
    mapsets = relationship("MapsetModel", lazy="selectin")
