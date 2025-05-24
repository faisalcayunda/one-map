from typing import List
from uuid import UUID

from fastapi_async_sqlalchemy import db
from sqlalchemy import update

from app.models import NewsModel

from . import BaseRepository


class NewsRepository(BaseRepository[NewsModel]):
    def __init__(self, model):
        super().__init__(model)

    async def bulk_update_activation(self, news_ids: List[UUID], is_active: bool) -> None:
        for news_id in news_ids:
            await db.session.execute(update(self.model).where(self.model.id == news_id).values(is_active=is_active))
        await db.session.commit()
