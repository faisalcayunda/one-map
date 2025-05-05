from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.data_types import UUID7Field
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.map_projection_system_schema import (
    MapProjectionSystemCreateSchema,
    MapProjectionSystemSchema,
    MapProjectionSystemUpdateSchema,
)
from app.services import MapProjectionSystemService

router = APIRouter()


@router.get("/map_projection_systems", response_model=PaginatedResponse[MapProjectionSystemSchema])
async def get_map_projection_systems(
    params: CommonParams = Depends(),
    service: MapProjectionSystemService = Depends(Factory().get_map_projection_system_service),
):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    map_projection_systems, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[
            MapProjectionSystemSchema.model_validate(map_projection_system)
            for map_projection_system in map_projection_systems
        ],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/map_projection_systems/{id}", response_model=MapProjectionSystemSchema)
async def get_map_projection_system(
    id: UUID7Field, service: MapProjectionSystemService = Depends(Factory().get_map_projection_system_service)
):
    map_projection_system = await service.find_by_id(id)
    return map_projection_system


@router.post(
    "/map_projection_systems",
    response_model=MapProjectionSystemSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_map_projection_system(
    data: MapProjectionSystemCreateSchema,
    service: MapProjectionSystemService = Depends(Factory().get_map_projection_system_service),
):
    map_projection_system = await service.create(data.dict())
    return map_projection_system


@router.patch(
    "/map_projection_systems/{id}",
    response_model=MapProjectionSystemSchema,
    dependencies=[Depends(get_current_active_user)],
)
async def update_map_projection_system(
    id: UUID7Field,
    data: MapProjectionSystemUpdateSchema,
    service: MapProjectionSystemService = Depends(Factory().get_map_projection_system_service),
):
    map_projection_system = await service.update(id, data.dict(exclude_unset=True))
    return map_projection_system


@router.delete(
    "/map_projection_systems/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)],
)
async def delete_map_projection_system(
    id: UUID7Field, service: MapProjectionSystemService = Depends(Factory().get_map_projection_system_service)
):
    await service.delete(id)
