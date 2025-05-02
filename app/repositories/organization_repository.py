from fastapi_async_sqlalchemy import db
from sqlalchemy import String, cast, select

from app.models.organization_model import OrganizationModel

from . import BaseRepository


class OrganizationRepository(BaseRepository[OrganizationModel]):
    def __init__(self, model):
        super().__init__(model)

    async def flag_delete_organization(self, id):
        return await self.flag_delete_organization(id)

    async def find_by_name(self, name: str, sensitive: bool = False):
        if not sensitive:
            name = name.lower()

        query = select(self.model)
        if not sensitive:
            query = query.where(cast(self.model.name, String).ilike(f"%{name}%"))
        else:
            query = query.where(self.model.name.ilike(f"%{name}%"))

        result = await db.session.execute(query)

        return result.scalar_one_or_none()
