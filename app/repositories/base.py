from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from fastapi_async_sqlalchemy import db
from sqlalchemy import String, cast
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import func, or_, select
from sqlalchemy import update as sqlalchemy_update
from uuid6 import UUID

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository for database operations using SQLAlchemy."""

    def __init__(self, model: Type[ModelType]):
        self.model: Type[ModelType] = model

    async def find_by_id(self, id: UUID) -> Optional[ModelType]:
        """Find a record by id."""
        query = select(self.model).where(self.model.id == id)
        if hasattr(self.model, "is_deleted"):
            query = query.where(self.model.is_deleted.is_(False))

        result = await db.session.execute(query)
        return result.scalar_one_or_none()

    async def find_all(
        self, filters: list, sort: list = [], search: str = "", group_by: str = None, limit: int = 100, offset: int = 0
    ) -> Tuple[List[ModelType], int]:
        """Find all records with pagination."""
        query = select(self.model)
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted.is_(False))

        query = query.filter(*filters)

        if search:
            query = query.filter(
                or_(
                    cast(getattr(self.model, col), String).ilike(f"%{search}%")
                    for col in self.model.__table__.columns.keys()
                )
            )

        if group_by:
            query = query.group_by(getattr(self.model, group_by))

        total = await db.session.scalar(select(func.count()).select_from(query.subquery()))

        query = query.order_by(*sort)
        query = query.limit(limit).offset(offset)

        result = await db.session.execute(query)
        result = result.scalars().all()

        return result, total

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        new_record = self.model(**data)
        db.session.add(new_record)
        await db.session.commit()
        await db.session.refresh(new_record)
        return new_record

    async def bulk_create(self, data: List[Dict[str, Any]]) -> None:
        """Create multiple records."""
        new_records = [self.model(**item) for item in data]
        db.session.add_all(new_records)
        await db.session.commit()

    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record."""
        query = (
            sqlalchemy_update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .execution_options(synchronize_session="fetch")
        )
        await db.session.execute(query)
        await db.session.commit()

        return await self.find_by_id(id)

    async def delete(self, id: UUID) -> None:
        """Delete a record."""
        query = sqlalchemy_delete(self.model).where(self.model.id == id)
        await db.session.execute(query)
        await db.session.commit()
