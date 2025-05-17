from datetime import datetime
from typing import Optional

from app.core.serializers import ORJSONBaseModel


class Token(ORJSONBaseModel):
    access_token: str
    refresh_token: str
    expires_at: float
    token_type: str = "bearer"


class TokenPayload(ORJSONBaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None


class RefreshTokenSchema(ORJSONBaseModel):
    refresh_token: str
