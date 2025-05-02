from typing import Dict, Optional

from fastapi import HTTPException, status
from uuid6 import UUID

from app.core.exceptions import NotFoundException
from app.models.organization_model import OrganizationModel
from app.repositories.organization_repository import OrganizationRepository

from . import BaseService


class OrganizationService(BaseService[OrganizationModel]):
    def __init__(self, repository: OrganizationRepository):
        super().__init__(OrganizationModel, repository)
        self.repository = repository

    async def get_organizations_by_id(self, id: UUID) -> Dict[str, str]:
        try:
            organization = await super().find_by_id(id)
            if organization is None:
                raise NotFoundException(f"Organization with UUID {id} not found.")

            return organization
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    async def find_by_name(self, name: str, sensitive: bool = False) -> Optional[OrganizationModel]:
        try:
            return await self.repository.find_by_name(name, sensitive)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    async def find_all(self, filters, sort, search="", group_by=None, limit=100, offset=0):
        return await super().find_all(filters, sort, search, group_by, limit, offset)

    async def create(self, data: Dict[str, str]) -> OrganizationModel:
        if await self.find_by_name(data["name"], True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Organization with this name already exists."
            )

        return await super().create(data)

    async def update(self, id: UUID, data: Dict[str, str]) -> OrganizationModel:
        organization = await self.find_by_id(id)
        if not organization:
            raise NotFoundException(f"Organization with UUID {id} not found.")

        if "name" in data and await self.find_by_name(data["name"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Organization with this name already exists."
            )

        return await super().update(id, data)

    async def delete(self, id: UUID) -> None:
        organization = await self.find_by_id(id)
        if not organization:
            raise NotFoundException(f"Organization with UUID {id} not found.")

        return await self.repository.delete(id)
