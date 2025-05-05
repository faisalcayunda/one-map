from datetime import datetime

import uuid6
from pytz import timezone
from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.config import settings

from . import Base


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)))

    user = relationship("UserModel", lazy="selectin", uselist=False)
