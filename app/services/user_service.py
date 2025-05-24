from typing import Dict, List

from fastapi import HTTPException, status
from uuid6 import UUID

from app.core.exceptions import NotFoundException
from app.core.security import get_password_hash
from app.models import UserModel
from app.repositories import UserRepository

from . import BaseService


class UserService(BaseService[UserModel]):
    def __init__(self, repository: UserRepository):
        super().__init__(UserModel, repository)
        self.repository = repository

    async def find_by_username(self, username: str) -> UserModel | None:
        user = await self.repository.find_by_username(username)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def find_by_email(self, email: str) -> UserModel | None:
        user = await self.repository.find_by_email(email)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def find_by_id(self, id: UUID) -> UserModel | None:
        user = await self.repository.find_by_id(id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def create(self, user_data: Dict) -> UserModel:
        if await self.repository.find_by_username(user_data["username"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        if await self.repository.find_by_email(user_data["email"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        user_data["password"] = get_password_hash(user_data["password"])
        return await self.repository.create(user_data)

    async def update(self, id: UUID, user_data: Dict) -> UserModel:
        user = await self.find_by_id(id)
        if not user:
            raise NotFoundException("User not found")

        if "username" in user_data and await self.repository.find_by_username(user_data["username"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        if "email" in user_data and await self.repository.find_by_email(user_data["email"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        if "password" in user_data:
            user_data["password"] = get_password_hash(user_data["password"])

        return await self.repository.update(id, user_data)

    async def bulk_update_activation(self, user_ids: List[UUID], is_active: bool) -> None:
        await self.repository.bulk_update_activation(user_ids, is_active)
