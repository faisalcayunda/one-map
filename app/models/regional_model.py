from datetime import datetime

import uuid6
from sqlalchemy import UUID, Boolean, Column, DateTime, String, Text

from . import Base


class RegionalModel(Base):
    __tablename__ = "regionals"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    code = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
