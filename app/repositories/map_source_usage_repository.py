from typing import Any, Dict, List
from uuid import UUID

from fastapi_async_sqlalchemy import db
from sqlalchemy import delete

from app.models import SourceUsageModel

from . import BaseRepository


class SourceUsageRepository(BaseRepository[SourceUsageModel]):
    def __init__(self, model):
        super().__init__(model)

    async def bulk_update(self, mapset_id: UUID, data: List[Dict[str, Any]]) -> None:
        """Update multiple records."""
        try:
            delete_query = delete(self.model).where(self.model.mapset_id == mapset_id)
            await db.session.execute(delete_query)

            new_records = [self.model(**item) for item in data]
            db.session.add_all(new_records)

            await db.session.commit()
        except Exception as e:
            await db.session.rollback()
            raise e
