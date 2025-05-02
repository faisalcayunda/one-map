import uuid6
from sqlalchemy import UUID, Boolean, Column, Integer, String, Text, text

from . import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String)
    description = Column(Text)
    thumbnail = Column(String)
    count_mapset = Column(Integer, default=0, server_default=text("0"))
    is_active = Column(Boolean, default=True)
