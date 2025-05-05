from datetime import datetime

import uuid6
from pytz import timezone
from sqlalchemy import UUID, Boolean, Column, DateTime, String, Text

from app.core.config import settings

from . import Base


class RegionalModel(Base):
    __tablename__ = "regionals"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    code = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)))
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )
