from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field, field_validator

from app.core.data_types import UUID7Field
from app.core.exceptions import UnprocessableEntity
from app.core.serializers import ORJSONBaseModel


class CredentialBase(ORJSONBaseModel):
    name: str = Field(..., description="Nama kredensial")
    description: Optional[str] = Field(None, description="Deskripsi kredensial")
    credential_type: str = Field(..., description="Tipe kredensial ('database', 'api', 'minio', dll)")
    credential_metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Metadata tidak sensitif (tidak dienkripsi)"
    )
    is_default: bool = Field(
        default=False, description="Apakah kredensial ini digunakan sebagai default untuk tipenya"
    )


class CredentialSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    description: Optional[str]
    credential_type: str
    credential_metadata: Optional[Dict[str, Any]]
    is_default: bool
    is_active: bool
    created_by: UUID7Field
    updated_by: Optional[UUID7Field]
    created_at: datetime
    updated_at: Optional[datetime]
    last_used_at: Optional[datetime]
    last_used_by: Optional[UUID7Field]


class CredentialWithSensitiveDataSchema(ORJSONBaseModel):
    id: UUID7Field
    name: str
    description: Optional[str]
    decrypted_data: Dict[str, Any]
    credential_type: str
    credential_metadata: Optional[Dict[str, Any]]
    is_default: bool
    is_active: bool
    created_by: UUID7Field
    updated_by: Optional[UUID7Field]
    created_at: datetime
    updated_at: Optional[datetime]
    last_used_at: Optional[datetime]
    last_used_by: Optional[UUID7Field]


class CredentialCreateSchema(CredentialBase):
    sensitive_data: Dict[str, Any] = Field(..., description="Data sensitif yang akan dienkripsi")


class CredentialUpdateSchema(ORJSONBaseModel):
    name: Optional[str] = Field(None, description="Nama kredensial")
    description: Optional[str] = Field(None, description="Deskripsi kredensial")
    credential_type: Optional[str] = Field(None, description="Tipe kredensial ('database', 'api', 'minio', dll)")
    credential_metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Metadata tidak sensitif (tidak dienkripsi)"
    )
    is_default: Optional[bool] = Field(
        default=False, description="Apakah kredensial ini digunakan sebagai default untuk tipenya"
    )
    sensitive_data: Optional[Dict[str, Any]] = Field(None, description="Data sensitif yang akan dienkripsi")

    @field_validator("credential_type")
    @classmethod
    def validate_credential_type(cls, v):
        allowed_types = {"database", "api", "minio", "ssh", "smtp", "ftp"}
        if v not in allowed_types:
            raise UnprocessableEntity(f'credential_type harus salah satu dari: {", ".join(allowed_types)}')
        return v

    @field_validator("sensitive_data")
    @classmethod
    def validate_sensitive_data(cls, v, values):
        """Validasi data sensitif berdasarkan tipe kredensial."""
        credential_type = values.data.get("credential_type", "")

        # Validasi untuk database
        if credential_type == "database":
            required_fields = {"host", "port", "username", "password", "database_name"}
            missing = required_fields - set(v.keys())
            if missing:
                raise UnprocessableEntity(f"Missing required fields for database: {', '.join(missing)}")

        # Validasi untuk MinIO
        elif credential_type == "minio":
            required_fields = {"endpoint", "access_key", "secret_key", "secure", "bucket_name"}
            missing = required_fields - set(v.keys())
            if missing:
                raise UnprocessableEntity(f"Missing required fields for minio: {', '.join(missing)}")

        # Validasi untuk API
        elif credential_type == "api":
            required_fields = {"base_url", "api_key"}
            missing = required_fields - set(v.keys())
            if missing:
                raise UnprocessableEntity(f"Missing required fields for api: {', '.join(missing)}")

        # Validasi untuk SSH
        elif credential_type == "ssh":
            if not ("password" in v or "private_key" in v):
                raise UnprocessableEntity("Either 'password' or 'private_key' is required for SSH credentials")

            required_fields = {"host", "port", "username"}
            missing = required_fields - set(v.keys())
            if missing:
                raise UnprocessableEntity(f"Missing required fields for ssh: {', '.join(missing)}")

        # Validasi untuk SMTP
        elif credential_type == "smtp":
            required_fields = {"host", "port", "username", "password", "use_tls"}
            missing = required_fields - set(v.keys())
            if missing:
                raise UnprocessableEntity(f"Missing required fields for smtp: {', '.join(missing)}")

        # Validasi untuk FTP
        elif credential_type == "ftp":
            required_fields = {"host", "port", "username", "password"}
            missing

        elif credential_type == "server":
            required_fields = {"host", "port", "username", "password"}
            missing = required_fields - set(v.keys())
            if missing:
                raise UnprocessableEntity(f"Missing required fields for server: {', '.join(missing)}")
