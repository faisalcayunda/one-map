from fastapi_async_sqlalchemy import db
from sqlalchemy import select

from app.models import FileModel

from . import BaseRepository


class FileRepository(BaseRepository[FileModel]):
    def __init__(self, model):
        super().__init__(model)

    async def find_by_user_id(self, user_id: int):
        query = select(self.model.user_id).where(self.model.user_id == user_id)
        result = await db.session.execute(query)
        return result.scalars().all()
