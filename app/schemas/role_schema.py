from typing import Optional

from pydantic import Field, field_validator

from app.core.data_types import UUID7Field
from app.core.exceptions import UnprocessableEntity
from app.core.serializers import ORJSONBaseModel


class RoleSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None)
    is_active: bool = True


class RoleCreateSchema(ORJSONBaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value

        valid_role = ["administrator", "data-validator", "data-manager", "data-observer"]
        if value not in valid_role:
            raise UnprocessableEntity(
                f"Role name must be one of the following: administrator, {', '.join(valid_role)}"
            )

        return value


class RoleUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None)
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value

        valid_role = ["administrator", "data-validator", "data-manager", "data-observer"]
        if value not in valid_role:
            raise UnprocessableEntity(
                f"Role name must be one of the following: administrator, {', '.join(valid_role)}"
            )

        return value
