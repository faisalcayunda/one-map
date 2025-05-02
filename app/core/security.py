# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def create_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None, token_type: str = "access"
) -> str:
    """Buat JWT token."""
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        if token_type == "access":
            expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == "refresh":
            expire = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expire = datetime.now() + timedelta(minutes=15)

    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_access_token(subject: Union[str, Any]) -> str:
    """Buat access token."""
    return create_token(subject, token_type="access")


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Buat refresh token."""
    return create_token(subject, token_type="refresh")


def decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT token."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload
