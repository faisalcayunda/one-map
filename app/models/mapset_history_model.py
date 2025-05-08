from datetime import datetime

import uuid6
from pytz import timezone
from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.config import settings

from . import Base


class MapsetHistoryModel(Base):
    """Model untuk melacak riwayat perubahan pada mapset."""

    __tablename__ = "mapset_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    mapset_id = Column(UUID(as_uuid=True), ForeignKey("mapsets.id"), index=True, comment="ID mapset yang dilacak")
    validation_type = Column(String(50), nullable=False, comment="Jenis perubahan pada mapset")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), comment="ID pengguna yang melakukan perubahan")
    notes = Column(Text, nullable=True, comment="Catatan detail perubahan yang dilakukan")
    timestamp = Column(
        DateTime(timezone=True), default=datetime.now(timezone(settings.TIMEZONE)), comment="Waktu perubahan tercatat"
    )

    user = relationship("UserModel", uselist=False, lazy="selectin")
