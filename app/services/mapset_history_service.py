from typing import Any, Dict

from app.models import MapsetHistoryModel
from app.repositories import MapsetHistoryRepository
from app.schemas.user_schema import UserSchema

from . import BaseService


class MapsetHistoryService(BaseService[MapsetHistoryModel]):
    def __init__(self, repository: MapsetHistoryRepository):
        super().__init__(MapsetHistoryModel, repository)
        self.repository = repository

    async def create(self, user: UserSchema, data: Dict[str, Any]) -> MapsetHistoryModel:
        data.update({"user_id": user.id})
        return await super().create(data)
