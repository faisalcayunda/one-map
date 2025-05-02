from app.models import MapAccessModel
from app.repositories import MapAccessRepository

from . import BaseService


class MapAccessService(BaseService[MapAccessModel]):
    def __init__(self, repository: MapAccessRepository):
        super().__init__(MapAccessModel, repository)
        self.repository = repository

    async def find_by_mapset(self, mapset_id: str):
        return await self.repository.find_by_mapset(mapset_id)

    async def find_by_user(self, user_id: str):
        return await self.repository.find_by_user(user_id)

    async def find_by_organization(self, organization_id: str):
        return await self.repository.find_by_organization(organization_id)

    async def find_user_access_to_mapset(self, mapset_id: str, user_id: str):
        return await self.repository.find_user_access_to_mapset(mapset_id, user_id)

    async def find_organization_access_to_mapset(self, mapset_id: str, organization_id: str):
        return await self.repository.find_organization_access_to_mapset(mapset_id, organization_id)
