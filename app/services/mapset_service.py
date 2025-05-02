import json
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
        filters: list[str],
        sort: list[str],
        search: str = "",
        group_by: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[MapsetModel], int]:
        list_model_filters = []
        list_sort = []

        for filter in filters:
            if filter.startswith("[") and filter.endswith("]"):
                try:
                    list_value = json.loads(filter)
                    if isinstance(list_value, list):
                        or_filter = []
                        for values in list_value:
                            col, value = values.split("=")
                            if not hasattr(self.model_class, col):
                                raise UnprocessableEntity(f"Invalid filter column: {col}")
                            if value.lower() in {"true", "false", "t", "f"}:
                                match value.lower():
                                    case "true" | "t":
                                        value = True
                                    case "false" | "f":
                                        value = False

                            or_filter.append(getattr(self.model_class, col) == value)
                        list_model_filters.append(or_(*or_filter))
                        continue
                except (json.JSONDecodeError, ValueError):
                    pass

            col, value = filter.split("=")
            if not hasattr(self.model_class, col):
                raise UnprocessableEntity(f"Invalid filter column: {col}")

            if value.lower() in {"true", "false", "t", "f"}:
                match value.lower():
                    case "true" | "t":
                        value = True
                    case "false" | "f":
                        value = False

                list_model_filters.append(getattr(self.model_class, col).is_(value))
            else:
                list_model_filters.append(getattr(self.model_class, col) == value)
        for s in sort:
            col, order = s.split(":")
            if not hasattr(self.model_class, col):
                raise UnprocessableEntity(f"Invalid sort column: {s}")

            if order.lower() == "asc":
                list_sort.append(getattr(self.model_class, col).asc())
            elif order.lower() == "desc":
                list_sort.append(getattr(self.model_class, col).desc())
            else:
                raise UnprocessableEntity(f"Invalid sort order for {s}")

        return await self.repository.find_all(user, list_model_filters, list_sort, search, group_by, limit, offset)

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
        # Pisahkan filter untuk mapset dan organization
        mapset_filters = []
        organization_filters = []
        list_sort = []

        # Proses filter
        filters = filters or []
        for filter_str in filters:
            if filter_str.startswith("[") and filter_str.endswith("]"):
                # Proses filter JSON array (OR)
                try:
                    list_value = json.loads(filter_str)
                    if isinstance(list_value, list):
                        mapset_or_conditions = []
                        org_or_conditions = []

                        for value_str in list_value:
                            col, value = value_str.split("=")
                            # Tentukan model mana yang memiliki kolom ini
                            if hasattr(MapsetModel, col):
                                # Konversi boolean jika perlu
                                if value.lower() in {"true", "false", "t", "f"}:
                                    value = value.lower() in {"true", "t"}
                                mapset_or_conditions.append(getattr(MapsetModel, col) == value)
                            elif hasattr(OrganizationModel, col):
                                if value.lower() in {"true", "false", "t", "f"}:
                                    value = value.lower() in {"true", "t"}
                                org_or_conditions.append(getattr(OrganizationModel, col) == value)
                            else:
                                raise UnprocessableEntity(f"Invalid filter column: {col}")

                        # Tambahkan kondisi OR ke daftar filter
                        if mapset_or_conditions:
                            mapset_filters.append(or_(*mapset_or_conditions))
                        if org_or_conditions:
                            organization_filters.append(or_(*org_or_conditions))
                        continue
                except (json.JSONDecodeError, ValueError):
                    raise UnprocessableEntity(f"Invalid JSON filter: {filter_str}")

            # Proses filter biasa (column=value)
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

        # Proses parameter sort
        for sort_str in sort or []:
            try:
                col, order = sort_str.split(":")

                # Tentukan model mana untuk sort
                if hasattr(OrganizationModel, col):
                    sort_col = getattr(OrganizationModel, col)
                elif hasattr(MapsetModel, col):
                    # Untuk sort berdasarkan atribut mapset, kita perlu subquery
                    # Ini tidak diimplementasi di sini untuk menjaga kesederhanaan
                    # Namun Anda bisa mengembangkannya jika diperlukan
                    continue
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

        # Default sort jika tidak ada
        if not list_sort:
            list_sort = [OrganizationModel.name.asc()]

        # Panggil repository dengan filter yang sudah diproses
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
