from typing import List

from fastapi import APIRouter, Body, Depends, status

from app.api.dependencies.auth import get_current_active_user, get_payload
from app.api.dependencies.factory import Factory
from app.core.data_types import UUID7Field
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.mapset_schema import (
    MapsetByOrganizationSchema,
    MapsetCreateSchema,
    MapsetSchema,
    MapsetUpdateSchema,
)
from app.schemas.user_schema import UserSchema
from app.services import MapsetService

router = APIRouter()


@router.get("/mapsets", response_model=PaginatedResponse[MapsetSchema])
async def get_mapsets(
    params: CommonParams = Depends(),
    user: UserSchema = Depends(get_payload),
    service: MapsetService = Depends(Factory().get_mapset_service),
):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    mapsets, total = await service.find_all(user, filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[MapsetSchema.model_validate(mapset) for mapset in mapsets],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/mapsets/organization", response_model=PaginatedResponse[MapsetByOrganizationSchema])
async def get_mapsets_organization(
    params: CommonParams = Depends(),
    user: UserSchema = Depends(get_payload),
    service: MapsetService = Depends(Factory().get_mapset_service),
):
    filter = params.filter
    sort = params.sort
    search = params.search
    limit = params.limit
    offset = params.offset
    mapsets, total = await service.find_all_group_by_organization(user, filter, sort, search, limit, offset)
    return PaginatedResponse(
        items=[MapsetByOrganizationSchema.model_validate(mapset) for mapset in mapsets],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/mapsets/{id}", response_model=MapsetSchema)
async def get_mapset(id: UUID7Field, service: MapsetService = Depends(Factory().get_mapset_service)):
    mapset = await service.find_by_id(id)
    return mapset


@router.post("/mapsets", response_model=MapsetSchema, status_code=status.HTTP_201_CREATED)
async def create_mapset(
    data: MapsetCreateSchema,
    user: UserSchema = Depends(get_current_active_user),
    service: MapsetService = Depends(Factory().get_mapset_service),
):
    mapset = await service.create(user, data.dict())
    return mapset


@router.post("/mapsets/color_scale", status_code=status.HTTP_200_OK)
async def create_color_scale(
    source_url: str = Body(..., embed=True),
    color_range: list[str] = Body(None, embed=True),
    service: MapsetService = Depends(Factory().get_mapset_service),
):
    result, rangelist = await service.generate_colorscale(source_url, color_range)
    return {"data": result, "rangelist": rangelist}


@router.patch(
    "/mapsets/activation", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def update_mapset_activation(
    ids: List[UUID7Field] = Body(...),
    is_active: bool = Body(...),
    service: MapsetService = Depends(Factory().get_mapset_service),
):
    await service.bulk_update_activation(ids, is_active)


@router.patch("/mapsets/{id}", response_model=MapsetSchema, dependencies=[Depends(get_payload)])
async def update_mapset(
    id: UUID7Field,
    data: MapsetUpdateSchema,
    user: UserSchema = Depends(get_current_active_user),
    service: MapsetService = Depends(Factory().get_mapset_service),
):
    mapset = await service.update(id, user, data.dict(exclude_unset=True))
    return mapset


@router.delete(
    "/mapsets/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def delete_mapset(id: UUID7Field, service: MapsetService = Depends(Factory().get_mapset_service)):
    await service.delete(id)
