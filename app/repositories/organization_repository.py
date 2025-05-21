from typing import List, Tuple

from fastapi_async_sqlalchemy import db
from sqlalchemy import (
    Integer,
    Numeric,
    String,
    Unicode,
    UnicodeText,
    and_,
    cast,
    func,
    or_,
    select,
)

from app.models.classification_model import ClassificationModel
from app.models.map_access_model import MapAccessModel
from app.models.mapset_model import MapsetModel
from app.models.organization_model import OrganizationModel
from app.schemas.user_schema import UserSchema

from . import BaseRepository


class OrganizationRepository(BaseRepository[OrganizationModel]):
    def __init__(self, model, mapset_model: MapsetModel):
        super().__init__(model)
        self.mapset_model = mapset_model

    async def flag_delete_organization(self, id):
        return await self.flag_delete_organization(id)

    async def find_by_name(self, name: str, sensitive: bool = False):
        if not sensitive:
            name = name.lower()

        query = select(self.model)
        if not sensitive:
            query = query.where(self.model.name == name)
        else:
            query = query.where(self.model.name.ilike(f"%{name}%"))

        result = await db.session.execute(query)

        return result.scalar_one_or_none()

    async def find_all(
        self,
        user: UserSchema | None,
        filters: list,
        sort: list | None = None,
        search: str = "",
        group_by: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[OrganizationModel], int]:
        """Find all records with pagination."""
        if sort is None:
            sort = []

        if user is None:
            mapset_filter = and_(
                ClassificationModel.is_open == True,
                self.mapset_model.is_active.is_(True),
                self.mapset_model.is_deleted.is_(False),
                self.mapset_model.producer_id == self.model.id,
            )
        elif user.role in {"administrator", "data_validator"}:
            mapset_filter = and_(
                self.mapset_model.is_active.is_(True),
                self.mapset_model.is_deleted.is_(False),
                self.mapset_model.producer_id == self.model.id,
            )
        else:
            mapset_filter = and_(
                or_(
                    ClassificationModel.is_limited.is_(True),
                    ClassificationModel.is_open.is_(True),
                    and_(
                        ClassificationModel.is_secret.is_(True),
                        self.mapset_model.producer_id == user.organization.id,
                    ),
                    and_(
                        ClassificationModel.is_secret.is_(True),
                        MapAccessModel.organization_id == user.organization.id,
                    ),
                    and_(
                        ClassificationModel.is_secret.is_(True),
                        MapAccessModel.user_id == user.id,
                    ),
                ),
                self.mapset_model.is_active.is_(True),
                self.mapset_model.is_deleted.is_(False),
                self.mapset_model.producer_id == self.model.id,
            )

        query = (
            select(
                self.model.id,
                self.model.name,
                self.model.description,
                self.model.thumbnail,
                self.model.address,
                self.model.phone_number,
                self.model.email,
                self.model.website,
                func.count(self.mapset_model.id).label("count_mapset"),
                self.model.is_active,
                self.model.is_deleted,
                self.model.created_at,
                self.model.modified_at,
            )
            .outerjoin(self.mapset_model, self.model.id == self.mapset_model.producer_id)
            .outerjoin(ClassificationModel, self.mapset_model.classification_id == ClassificationModel.id)
        )

        if user is not None and user.role not in {"administrator", "data_validator"}:
            query = query.outerjoin(MapAccessModel, self.mapset_model.id == MapAccessModel.mapset_id)

        if user is None or user.role not in {"administrator", "data_validator"}:
            query = query.where(mapset_filter)

        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted.is_(False))

        if filters:
            query = query.filter(*filters)

        if search:
            search_filters = []
            for col in self.model.__table__.columns.keys():
                column = getattr(self.model, col)
                if isinstance(column.type, (String, Unicode, UnicodeText)):
                    search_filters.append(column.ilike(f"%{search}%"))
                elif isinstance(column.type, (Integer, Numeric)):
                    try:
                        num_val = float(search)
                        search_filters.append(cast(column, String) == str(num_val))
                    except (ValueError, TypeError):
                        pass

            if search_filters:
                query = query.filter(or_(*search_filters))

        group_columns = [self.model.id]
        if group_by and hasattr(self.model, group_by):
            group_col = getattr(self.model, group_by)
            if group_col not in group_columns:
                group_columns.append(group_col)

        query = query.group_by(*group_columns)

        count_query = select(func.count()).select_from(
            select(self.model.id)
            .outerjoin(self.mapset_model, self.model.id == self.mapset_model.producer_id)
            .outerjoin(ClassificationModel, self.mapset_model.classification_id == ClassificationModel.id)
        )

        if user is not None and user.role not in {"administrator", "data_validator"}:
            count_query = count_query.select_from(
                count_query.subquery().select_from.outerjoin(
                    MapAccessModel, self.mapset_model.id == MapAccessModel.mapset_id
                )
            )

        if user is None or user.role not in {"administrator", "data_validator"}:
            count_query = count_query.where(mapset_filter)

        if hasattr(self.model, "is_deleted"):
            count_query = count_query.where(self.model.is_deleted.is_(False))

        if filters:
            count_query = count_query.where(*filters)

        if search and search_filters:
            count_query = count_query.where(or_(*search_filters))

        count_query = count_query.group_by(self.model.id)

        total = await db.session.scalar(select(func.count()).select_from(count_query.subquery()))

        if sort:
            query = query.order_by(*sort)

        query = query.limit(limit).offset(offset)

        result = await db.session.execute(query)
        result = result.mappings().all()

        return result, total
