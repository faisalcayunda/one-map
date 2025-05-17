from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import HTTPException, status
from pytz import timezone
from uuid6 import UUID

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user_model import UserModel
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    tz = timezone(settings.TIMEZONE)

    def __init__(self, user_repository: UserRepository, token_repository: TokenRepository):
        self.user_repository = user_repository
        self.token_repository = token_repository

    async def authenticate_user(self, username: str, password: str) -> Optional[UserModel]:
        """Autentikasi user dengan username dan password."""
        user = await self.user_repository.find_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def create_tokens(self, user_id: UUID) -> Dict[str, str]:
        """Buat access dan refresh token."""
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        now = datetime.now(timezone(settings.TIMEZONE))

        refresh_expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        expire_time = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_expires_at = expire_time.timestamp()

        refresh_token_data = {
            "user_id": user_id,
            "token": refresh_token,
            "expires_at": refresh_expires_at,
        }
        await self.token_repository.create(refresh_token_data)

        return {"access_token": access_token, "refresh_token": refresh_token, "expires_at": access_expires_at}

    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token menggunakan refresh token."""
        try:
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

            token_obj = await self.token_repository.find_valid_token(refresh_token, UUID(user_id))
            if not token_obj:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or expired"
                )

            await self.token_repository.revoke_token(refresh_token)

            return await self.create_tokens(UUID(user_id))

        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials")

    async def logout(self, refresh_token: str) -> bool:
        """Logout user dengan merevoke refresh token."""
        return await self.token_repository.revoke_token(refresh_token)
