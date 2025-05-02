import re
from typing import Optional

from pydantic import EmailStr, Field, field_validator

from app.core.data_types import UUID7Field
from app.core.exceptions import UnprocessableEntity
from app.core.serializers import ORJSONBaseModel

from .organization_schema import OrganizationSchema
from .role_schema import RoleSchema


class UserSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    email: EmailStr
    profile_picture: Optional[str] = None
    username: str
    position: Optional[str] = None
    role: RoleSchema
    employee_id: Optional[str] = None
    organization: OrganizationSchema
    is_active: bool = True


class UserCreateSchema(ORJSONBaseModel):
    name: str = Field(..., min_length=4, max_length=100)
    email: EmailStr
    profile_picture: Optional[str] = Field(None)
    username: str = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)
    position: Optional[str] = Field(None)
    role_id: UUID7Field
    employee_id: Optional[str] = None
    organization_id: UUID7Field
    is_active: bool = True

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if value is None:
            return value

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", value):
            raise UnprocessableEntity(
                "Password must be at least 8 characters long and contain at least one letter, one number, and one special character"
            )

        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if value is None:
            return value

        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise UnprocessableEntity("Username can only contain letters, numbers, and underscores")

        return value

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, value):
        if value is None:
            return value

        # Validasi tambahan untuk domain email jika diperlukan
        value.split("@")[1]
        valid_domains = ["gmail.com", "yahoo.com", "hotmail.com", "company.com"]  # Sesuaikan dengan kebutuhan

        # Hapus validasi ini jika tidak diperlukan atau sesuaikan dengan kebutuhan
        # if domain not in valid_domains:
        #     raise UnprocessableEntity(f'Domain email tidak valid. Domain yang diizinkan: {", ".join(valid_domains)}')

        return value


class UserUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    position: Optional[str] = Field(None)
    role_id: Optional[UUID7Field] = Field(None)
    employee_id: Optional[str] = Field(None, max_length=50)
    organization_id: Optional[UUID7Field] = Field(None)
    is_active: Optional[bool] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if value is None:
            return value

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", value):
            raise UnprocessableEntity(
                "Password must be at least 8 characters long and contain at least one letter, one number, and one special character"
            )

        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value):
        if value is None:
            return value

        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise UnprocessableEntity("Username can only contain letters, numbers, and underscores")

        return value

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, value):
        if value is None:
            return value

        # Validasi tambahan untuk domain email jika diperlukan
        value.split("@")[1]
        valid_domains = ["gmail.com", "yahoo.com", "hotmail.com", "company.com"]  # Sesuaikan dengan kebutuhan

        # Hapus validasi ini jika tidak diperlukan atau sesuaikan dengan kebutuhan
        # if domain not in valid_domains:
        #     raise UnprocessableEntity(f'Domain email tidak valid. Domain yang diizinkan: {", ".join(valid_domains)}')

        return value
