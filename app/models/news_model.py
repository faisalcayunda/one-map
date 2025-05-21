from datetime import datetime

import uuid6
from pytz import timezone
from sqlalchemy import UUID, Boolean, Column, DateTime, String, Text, func

from app.core.config import settings

from . import Base


class NewsModel(Base):
    __tablename__ = "news"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String)
    description = Column(Text)
    thumbnail = Column(String)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now(timezone(settings.TIMEZONE))
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=datetime.now(timezone(settings.TIMEZONE)),
    )
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
