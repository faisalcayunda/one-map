from typing import List

from fastapi_async_sqlalchemy import db
from sqlalchemy import select, update
from uuid6 import UUID

from app.models import UserModel

from . import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, model):
        super().__init__(model)

    async def find_by_username(self, username: str) -> UserModel | None:
        query = select(self.model).filter(self.model.username == username)
        result = await db.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> UserModel | None:
        query = select(self.model).filter(self.model.email == email)
        result = await db.session.execute(query)
        return result.scalar_one_or_none()

    async def find_by_id(self, id: UUID) -> UserModel | None:
        query = select(self.model).filter(self.model.id == id)
        result = await db.session.execute(query)
        return result.scalar_one_or_none()

    async def bulk_update_activation(self, user_ids: List[UUID], is_active: bool) -> None:
        for user_id in user_ids:
            await db.session.execute(update(self.model).where(self.model.id == user_id).values(is_active=is_active))
        await db.session.commit()
