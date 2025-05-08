from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import or_
from uuid6 import UUID

from app.core.exceptions import UnprocessableEntity
from app.models import MapsetModel
from app.models.organization_model import OrganizationModel
from app.repositories import MapsetRepository
from app.schemas.user_schema import UserSchema

from . import BaseService


class MapsetService(BaseService[MapsetModel]):
    def __init__(self, repository: MapsetRepository):
        super().__init__(MapsetModel, repository)
        self.repository = repository

    async def find_all(
        self,
        user: UserSchema,
        filters: str | List[str],
        sort: str | List[str],
        search: str = "",
        group_by: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[MapsetModel] | int]:
        return await self.repository.find_all(user, filters, sort, search, group_by, limit, offset)

    async def find_all_group_by_organization(
        self,
        user: Optional[UserSchema] = None,
        filters: Optional[list[str]] = None,
        sort: Optional[list[str]] = None,
        search: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Dict], int]:
        """
        Find organizations with filtered mapsets.
        Only returns the mapsets that match the filter for each organization.
        """
        mapset_filters = []
        organization_filters = []
        list_sort = []

        filters = filters or []

        if isinstance(filters, str):
            filters = [filters]

        for filter_str in filters:
            if isinstance(filter_str, list):
                mapset_or_conditions = []
                org_or_conditions = []

                for value_str in filter_str:
                    col, value = value_str.split("=")
                    if hasattr(MapsetModel, col):
                        if value.lower() in {"true", "false", "t", "f"}:
                            value = value.lower() in {"true", "t"}
                        mapset_or_conditions.append(getattr(MapsetModel, col) == value)
                    elif hasattr(OrganizationModel, col):
                        if value.lower() in {"true", "false", "t", "f"}:
                            value = value.lower() in {"true", "t"}
                        org_or_conditions.append(getattr(OrganizationModel, col) == value)
                    else:
                        raise UnprocessableEntity(f"Invalid filter column: {col}")

                if mapset_or_conditions:
                    mapset_filters.append(or_(*mapset_or_conditions))
                if org_or_conditions:
                    organization_filters.append(or_(*org_or_conditions))
                continue

            try:
                col, value = filter_str.split("=")

                # Konversi nilai boolean jika perlu
                if value.lower() in {"true", "false", "t", "f"}:
                    value = value.lower() in {"true", "t"}

                # Tambahkan filter ke daftar yang sesuai
                if hasattr(MapsetModel, col):
                    mapset_filters.append(getattr(MapsetModel, col) == value)
                elif hasattr(OrganizationModel, col):
                    organization_filters.append(getattr(OrganizationModel, col) == value)
                else:
                    raise UnprocessableEntity(f"Invalid filter column: {col}")
            except ValueError:
                raise UnprocessableEntity(f"Invalid filter format: {filter_str}")

        if isinstance(sort, str):
            sort = [sort]

        for sort_str in sort or []:
            try:
                col, order = sort_str.split(":")

                if hasattr(OrganizationModel, col):
                    sort_col = getattr(OrganizationModel, col)
                elif hasattr(MapsetModel, col):
                    # Untuk sort berdasarkan atribut mapset, kita perlu subquery
                    # Ini tidak diimplementasi di sini untuk menjaga kesederhanaan
                    # Namun Anda bisa mengembangkannya jika diperlukan
                    # continue
                    sort_col = getattr(MapsetModel, col)
                else:
                    raise UnprocessableEntity(f"Invalid sort column: {col}")

                if order.lower() == "asc":
                    list_sort.append(sort_col.asc())
                elif order.lower() == "desc":
                    list_sort.append(sort_col.desc())
                else:
                    raise UnprocessableEntity(f"Invalid sort order: {order}")
            except ValueError:
                raise UnprocessableEntity(f"Invalid sort format: {sort_str}")

        if not list_sort:
            list_sort = [OrganizationModel.name.asc()]

        return await self.repository.find_all_group_by_organization(
            user=user,
            mapset_filters=mapset_filters,
            organization_filters=organization_filters,
            sort=list_sort,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def create(self, user: UserSchema, data: Dict[str, Any]) -> MapsetModel:
        data["created_by"] = user.id
        data["updated_by"] = user.id
        return await super().create(data)

    async def update(self, id: UUID, user: UserSchema, data: Dict[str, Any]) -> MapsetModel:
        data["updated_by"] = user.id
        return await super().update(id, data)
