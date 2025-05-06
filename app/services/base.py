import json
from typing import Any, Dict, Generic, List, Tuple, Type, TypeVar

from sqlalchemy import or_
from uuid6 import UUID

from app.core.database import Base
from app.core.exceptions import NotFoundException, UnprocessableEntity
from app.repositories import BaseRepository

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """Base class for data controllers."""

    def __init__(self, model: Type[ModelType], repository: BaseRepository):
        self.model_class = model
        self.repository = repository

    async def find_by_id(self, id: UUID) -> ModelType:
        """Find a record by UUID."""
        record = await self.repository.find_by_id(id)
        if not record:
            raise NotFoundException(f"{self.model_class.__name__} with UUID {id} not found.")

        return record

    async def find_all(
        self,
        filters: list[str],
        sort: list[str],
        search: str = "",
        group_by: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[ModelType], int]:
        """Find all records with optional grouping."""
        list_model_filters = []
        list_sort = []

        for filter in filters:
            if filter.startswith("[") and filter.endswith("]"):
                try:
                    list_value = json.loads(filter)
                    if isinstance(list_value, list):
                        or_filter = []
                        for values in list_value:
                            try:
                                col, value = values.split("=")
                            except ValueError:
                                raise UnprocessableEntity(
                                    f"Invalid filter {filter} must be 'name=value' or '[[name=value],[name=value]]'"
                                )

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

            try:
                col, value = filter.split("=")
            except ValueError:
                raise UnprocessableEntity(
                    f"Invalid filter {filter} must be 'name=value' or '[[name=value],[name=value]]'"
                )

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
            try:
                col, order = s.split(":")
            except ValueError:
                raise UnprocessableEntity(f"Invalid sort {s} Must be 'name:asc' or 'name:desc'")

            if not hasattr(self.model_class, col):
                raise UnprocessableEntity(f"Invalid sort column: {s}")

            if order.lower() == "asc":
                list_sort.append(getattr(self.model_class, col).asc())
            elif order.lower() == "desc":
                list_sort.append(getattr(self.model_class, col).desc())
            else:
                raise UnprocessableEntity(f"Invalid sort order for {s}")

        return await self.repository.find_all(
            filters=list_model_filters, sort=list_sort, search=search, group_by=group_by, limit=limit, offset=offset
        )

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        return await self.repository.create(data)

    async def update(self, id: UUID, data: Dict[str, Any]) -> ModelType:
        """Update an existing record."""
        instance = await self.find_by_id(id)
        if not instance:
            raise NotFoundException(f"{self.model_class.__name__} with UUID {id} not found.")

        return await self.repository.update(id, data)

    async def delete(self, id: UUID) -> None:
        """Delete a record by UUID."""
        instance = await self.find_by_id(id)
        if not instance:
            raise NotFoundException(f"{self.model_class.__name__} with UUID {id} not found.")

        await self.repository.delete(id)
