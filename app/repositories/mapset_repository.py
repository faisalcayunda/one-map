from ast import Dict
from typing import List, Optional, Tuple

from fastapi_async_sqlalchemy import db
from sqlalchemy import String, and_, cast, func, or_, select
from sqlalchemy.orm import selectinload

from app.models import (
    ClassificationModel,
    MapAccessModel,
    MapsetModel,
    OrganizationModel,
)
from app.schemas.user_schema import UserSchema

from . import BaseRepository


class MapsetRepository(BaseRepository[MapsetModel]):
    def __init__(self, model):
        super().__init__(model)

    async def find_all(
        self,
        user: UserSchema = None,
        filters: list = None,
        sort: list = ...,
        search: str = "",
        group_by: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[MapsetModel], int]:

        if user is None:
            query = (
                select(self.model)
                .distinct()
                .join(ClassificationModel, self.model.classification_id == ClassificationModel.id)
                .filter(ClassificationModel.is_open == True)
            )
        elif user.role in {"administrator", "data_validator"}:
            query = select(self.model)
        else:
            query = (
                select(self.model)
                .distinct()
                .join(MapAccessModel, self.model.id == MapAccessModel.mapset_id, isouter=True)
                .join(ClassificationModel, self.model.classification_id == ClassificationModel.id)
                .filter(
                    or_(
                        ClassificationModel.is_limited.is_(True),
                        ClassificationModel.is_open.is_(True),
                        and_(
                            ClassificationModel.is_secret.is_(True),
                            self.model.producer_id == user.organization.id,
                        ),
                        and_(
                            ClassificationModel.is_secret.is_(True),
                            MapAccessModel.organization_id == user.organization.id,
                        ),
                        and_(
                            ClassificationModel.is_secret.is_(True),
                            MapAccessModel.user_id == user.id,
                        ),
                    )
                )
            )

        query = query.filter(*filters)

        if search:
            query = query.filter(
                or_(
                    or_(
                        cast(getattr(self.model, col), String).ilike(f"%{search}%")
                        for col in self.model.__table__.columns.keys()
                    ),
                    OrganizationModel.name.ilike(f"%{search}%"),
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

    async def find_all_group_by_organization(
        self,
        user: Optional[UserSchema] = None,
        mapset_filters: list = None,
        organization_filters: list = None,
        sort: list = None,
        search: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Dict], int]:

        mapset_filters = mapset_filters or []
        organization_filters = organization_filters or []
        sort = sort or [OrganizationModel.name.asc()]

        if user is None:
            base_mapset_query = (
                select(self.model)
                .join(ClassificationModel, self.model.classification_id == ClassificationModel.id)
                .filter(ClassificationModel.is_open.is_(True))
            )
        elif user.role in {"administrator", "data-validator"}:
            base_mapset_query = select(self.model)
        else:
            user_org_id = user.organization.id if user.organization else None

            base_mapset_query = (
                select(self.model)
                .join(ClassificationModel, self.model.classification_id == ClassificationModel.id)
                .outerjoin(MapAccessModel, self.model.id == MapAccessModel.mapset_id)
                .filter(
                    or_(
                        ClassificationModel.is_open.is_(True),
                        ClassificationModel.is_limited.is_(True),
                        and_(
                            ClassificationModel.is_secret.is_(True),
                            self.model.producer_id == user.id,
                        ),
                        and_(
                            ClassificationModel.is_secret.is_(True),
                            MapAccessModel.user_id == user.id,
                        ),
                        and_(
                            ClassificationModel.is_secret.is_(True),
                            user_org_id is not None,
                            MapAccessModel.organization_id == user_org_id,
                        ),
                    )
                )
            )

        filtered_mapset_query = base_mapset_query
        if mapset_filters:
            filtered_mapset_query = filtered_mapset_query.filter(*mapset_filters)

        if search:
            search_filters = []
            for col in self.model.__table__.columns.keys():
                if hasattr(self.model, col):
                    search_filters.append(cast(getattr(self.model, col), String).ilike(f"%{search}%"))

            if search_filters:
                filtered_mapset_query = filtered_mapset_query.filter(or_(*search_filters))

        producer_ids_subquery = select(self.model.producer_id).select_from(filtered_mapset_query.subquery()).distinct()

        org_query = select(OrganizationModel).filter(OrganizationModel.id.in_(producer_ids_subquery))

        if organization_filters:
            org_query = org_query.filter(*organization_filters)

        if search:
            org_search_filters = []
            for col in OrganizationModel.__table__.columns.keys():
                if hasattr(OrganizationModel, col):
                    org_search_filters.append(cast(getattr(OrganizationModel, col), String).ilike(f"%{search}%"))

            if org_search_filters:
                org_query = org_query.filter(or_(*org_search_filters))

        count_query = select(func.count()).select_from(
            select(OrganizationModel.id).select_from(org_query.subquery()).distinct()
        )
        total = await db.session.scalar(count_query)

        org_query = org_query.order_by(*sort)

        if limit:
            org_query = org_query.limit(limit)
        if offset:
            org_query = org_query.offset(offset)

        org_result = await db.session.execute(org_query)
        organizations = org_result.scalars().unique().all()

        org_ids = [org.id for org in organizations]

        if not org_ids:
            return [], total

        all_mapsets_query = filtered_mapset_query.filter(self.model.producer_id.in_(org_ids)).options(
            selectinload(self.model.classification)
        )

        all_mapsets_result = await db.session.execute(all_mapsets_query)
        all_mapsets = all_mapsets_result.scalars().unique().all()

        mapsets_by_org = {}
        for mapset in all_mapsets:
            if mapset.producer_id not in mapsets_by_org:
                mapsets_by_org[mapset.producer_id] = []
            mapsets_by_org[mapset.producer_id].append(mapset)

        result_data = []
        for org in organizations:
            org_mapsets = mapsets_by_org.get(org.id, [])

            result_data.append({"id": org.id, "name": org.name, "mapsets": org_mapsets, "found": len(org_mapsets)})

        return result_data, total
