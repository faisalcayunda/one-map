from datetime import datetime

import uuid6
from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from . import Base


class FileModel(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7, index=True)
    filename = Column(String(255), nullable=False, index=True)
    object_name = Column(String(512), nullable=False, unique=True)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1024), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    modified_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    uploaded_by = relationship("UserModel", lazy="selectin", uselist=False)
