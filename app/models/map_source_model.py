from datetime import datetime

import uuid6
from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String, Text

from . import Base


class MapSourceModel(Base):
    __tablename__ = "map_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    credential_id = Column(UUID(as_uuid=True), ForeignKey("credentials.id"))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
