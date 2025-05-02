import uuid6
from sqlalchemy import UUID, Boolean, Column, String

from . import Base


class ClassificationModel(Base):
    __tablename__ = "classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String(20), nullable=False)
    is_open = Column(Boolean, default=True)
    is_limited = Column(Boolean, default=False)
    is_secret = Column(Boolean, default=False)
