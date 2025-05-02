import uuid6
from sqlalchemy import UUID, Boolean, Column, String, Text

from . import Base


class NewsModel(Base):
    __tablename__ = "news"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String)
    description = Column(Text)
    thumbnail = Column(String)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
