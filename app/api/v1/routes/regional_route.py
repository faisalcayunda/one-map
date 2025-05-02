from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas import RegionalCreateSchema, RegionalSchema, RegionalUpdateSchema
from app.services import RegionalService

router = APIRouter()


@router.get("/regionals", response_model=PaginatedResponse[RegionalSchema])
async def get_regionals(
    params: CommonParams = Depends(), service: RegionalService = Depends(Factory().get_regional_service)
):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    regionals, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[RegionalSchema.model_validate(regional) for regional in regionals],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/regionals/{id}", response_model=RegionalSchema)
async def get_regional(id: str, service: RegionalService = Depends(Factory().get_regional_service)):
    regional = await service.find_by_id(id)
    return regional


@router.post(
    "/regionals",
    response_model=RegionalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_regional(
    data: RegionalCreateSchema, service: RegionalService = Depends(Factory().get_regional_service)
):
    regional = await service.create(data.dict())
    return regional


@router.patch("/regionals/{id}", response_model=RegionalSchema, dependencies=[Depends(get_current_active_user)])
async def update_regional(
    id: str,
    data: RegionalUpdateSchema,
    service: RegionalService = Depends(Factory().get_regional_service),
):
    regional = await service.update(id, data.dict(exclude_unset=True))
    return regional


@router.delete(
    "/regionals/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def delete_regional(id: str, service: RegionalService = Depends(Factory().get_regional_service)):
    await service.delete(id)
