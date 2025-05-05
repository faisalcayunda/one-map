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
    credential_id = Column(UUID(as_uuid=True), ForeignKey("credentials.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)))
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone(settings.TIMEZONE)),
        onupdate=datetime.now(timezone(settings.TIMEZONE)),
    )

    credential = relationship("CredentialModel", lazy="selectin", uselist=False)