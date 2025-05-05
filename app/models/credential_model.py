from datetime import datetime

import uuid6
from sqlalchemy import JSON, UUID, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped

from . import Base


class CredentialModel(Base):
    __tablename__ = "credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String)
    description = Column(Text)
    encrypted_data = Column(Text, nullable=False)
    encryption_iv = Column(String(255), nullable=False)
    credential_type = Column(String(50), nullable=False)
    credential_metadata: Mapped[dict] = Column(JSON, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_used_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
