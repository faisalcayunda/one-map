from typing import List
from uuid import UUID

from app.models import NewsModel
from app.repositories import NewsRepository

from . import BaseService


class NewsService(BaseService[NewsModel]):
    def __init__(self, repository: NewsRepository):
        super().__init__(NewsModel, repository)
        self.repository = repository

    async def bulk_update_activation(self, news_ids: List[UUID], is_active: bool) -> None:
        await self.repository.bulk_update_activation(news_ids, is_active)
