from fastapi_async_sqlalchemy import db
from sqlalchemy import select
from uuid6 import UUID

from app.models import MapAccessModel

from . import BaseRepository


class MapAccessRepository(BaseRepository[MapAccessModel]):
    def __init__(self, model):
        super().__init__(model)

    async def find_by_mapset(self, mapset_id: UUID):
        query = select(self.model).where(self.model.mapset_id == mapset_id)
        result = await db.session.execute(query)
        return result.scalars().all()

    async def find_by_user(self, user_id: UUID):
        query = select(self.model).where(self.model.user_id == user_id)
        result = await db.session.execute(query)
        return result.scalars().all()

    async def find_by_organization(self, organization_id: UUID):
        query = select(self.model).where(self.model.organization_id == organization_id)
        result = await db.session.execute(query)
        return result.scalars().all()

    async def find_user_access_to_mapset(self, mapset_id: UUID, user_id: UUID):
        query = select(self.model).where(self.model.mapset_id == mapset_id, self.model.user_id == user_id)
        result = await db.session.execute(query)
        return result.scalars().all()

    async def find_organization_access_to_mapset(self, mapset_id: UUID, organization_id: UUID):
        query = select(self.model).where(
            self.model.mapset_id == mapset_id, self.model.organization_id == organization_id
        )
        result = await db.session.execute(query)
        return result.scalars().all()
