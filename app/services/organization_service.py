from typing import Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from uuid6 import UUID

from app.core.exceptions import NotFoundException, UnprocessableEntity
from app.models.organization_model import OrganizationModel
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.user_schema import UserSchema

from . import BaseService


class OrganizationService(BaseService[OrganizationModel]):
    def __init__(self, repository: OrganizationRepository):
        super().__init__(OrganizationModel, repository)
        self.repository = repository

    async def get_organizations_by_id(self, user: UserSchema, id: UUID) -> Dict[str, str]:
        try:
            organization = await self.repository.find_by_id(user, id)
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

    async def find_all(self, user: UserSchema | None, filters, sort, search="", group_by=None, limit=100, offset=0):
        list_model_filters = []
        list_sort = []

        if isinstance(filters, str):
            filters = [filters]

        if hasattr(self.model_class, "is_deleted"):
            filters.append("is_deleted=false")

        for filter_item in filters:
            if isinstance(filter_item, list):
                or_filter = []
                for values in filter_item:
                    try:
                        col, value = values.split("=")
                    except ValueError:
                        raise UnprocessableEntity(
                            f"Invalid filter {filter_item} must be 'name=value' or '[[name=value],[name=value]]'"
                        )

                    if not hasattr(self.model_class, col):
                        raise UnprocessableEntity(f"Invalid filter column: {col}")

                    if col == "id":
                        try:
                            value = UUID(value)
                        except:
                            raise UnprocessableEntity(f"Invalid filter value {value}, please provide UUID")

                    if isinstance(value, str) and value.lower() in {"true", "false", "t", "f"}:
                        value = value.lower() in {"true", "t"}

                    or_filter.append(getattr(self.model_class, col) == value)
                list_model_filters.append(or_(*or_filter))
                continue

            try:
                col, value = filter_item.split("=")
            except ValueError:
                raise UnprocessableEntity(
                    f"Invalid filter {filter_item} must be 'name=value' or '[[name=value],[name=value]]'"
                )

            if not hasattr(self.model_class, col):
                raise UnprocessableEntity(f"Invalid filter column: {col}")

            if col == "id":
                try:
                    value = UUID(value)
                except:
                    raise UnprocessableEntity(f"Invalid filter value {value}, please provide UUID")

            if isinstance(value, str) and value.lower() in {"true", "false", "t", "f"}:
                value = value.lower() in {"true", "t"}
                list_model_filters.append(getattr(self.model_class, col).is_(value))
            else:
                list_model_filters.append(getattr(self.model_class, col) == value)

        if isinstance(sort, str):
            sort = [sort]

        for sort_item in sort:
            try:
                col, order = sort_item.split(":")
            except ValueError:
                raise UnprocessableEntity(f"Invalid sort {sort_item}. Must be 'name:asc' or 'name:desc'")

            if not hasattr(self.model_class, col):
                raise UnprocessableEntity(f"Invalid sort column: {col}")

            if order.lower() == "asc":
                list_sort.append(getattr(self.model_class, col).asc())
            elif order.lower() == "desc":
                list_sort.append(getattr(self.model_class, col).desc())
            else:
                raise UnprocessableEntity(f"Invalid sort order '{order}' for {col}")

        return await self.repository.find_all(
            user,
            filters=list_model_filters,
            sort=list_sort,
            search=search,
            group_by=group_by,
            limit=limit,
            offset=offset,
        )

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
