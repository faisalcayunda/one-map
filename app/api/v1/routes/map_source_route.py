from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.map_source_schema import (
    MapSourceCreateSchema,
    MapSourceSchema,
    MapSourceUpdateSchema,
)
from app.services import MapSourceService

router = APIRouter()


@router.get("/map_sources", response_model=PaginatedResponse[MapSourceSchema])
async def get_mapSources(
    params: CommonParams = Depends(), service: MapSourceService = Depends(Factory().get_map_source_service)
):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    mapSources, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[MapSourceSchema.model_validate(mapSource) for mapSource in mapSources],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/map_sources/{id}", response_model=MapSourceSchema)
async def get_mapSource(id: str, service: MapSourceService = Depends(Factory().get_map_source_service)):
    mapSource = await service.find_by_id(id)
    return mapSource


@router.post(
    "/map_sources",
    response_model=MapSourceSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_mapSource(
    data: MapSourceCreateSchema, service: MapSourceService = Depends(Factory().get_map_source_service)
):
    mapSource = await service.create(data.dict())
    return mapSource


@router.patch("/map_sources/{id}", response_model=MapSourceSchema, dependencies=[Depends(get_current_active_user)])
async def update_mapSource(
    id: str,
    data: MapSourceUpdateSchema,
    service: MapSourceService = Depends(Factory().get_map_source_service),
):
    mapSource = await service.update(id, data.dict(exclude_unset=True))
    return mapSource


@router.delete(
    "/map_sources/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def delete_mapSource(id: str, service: MapSourceService = Depends(Factory().get_map_source_service)):
    await service.delete(id)
