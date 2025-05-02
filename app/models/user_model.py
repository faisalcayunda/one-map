from datetime import datetime

import uuid6
from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from . import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid6.uuid7)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    profile_picture = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    position = Column(String, nullable=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    employee_id = Column(String, nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    modified_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    organization = relationship("OrganizationModel", back_populates="users", lazy="selectin", uselist=False)
    role = relationship("RoleModel", back_populates="users", lazy="selectin", uselist=False)
