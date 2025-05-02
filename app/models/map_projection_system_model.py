import uuid6
from sqlalchemy import UUID, Column, String

from . import Base


class MapProjectionSystemModel(Base):
    __tablename__ = "map_projection_systems"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String(50), nullable=False)
