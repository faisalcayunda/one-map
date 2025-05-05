from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.data_types import UUID7Field
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.category_schema import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)
from app.services import CategoryService

router = APIRouter()


@router.get("/categories", response_model=PaginatedResponse[CategorySchema])
async def get_categorys(
    params: CommonParams = Depends(), service: CategoryService = Depends(Factory().get_category_service)
):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    categorys, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[CategorySchema.model_validate(category) for category in categorys],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/categories/{id}", response_model=CategorySchema)
async def get_category(id: UUID7Field, service: CategoryService = Depends(Factory().get_category_service)):
    category = await service.find_by_id(id)
    return category


@router.post(
    "/categories",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_category(
    data: CategoryCreateSchema, service: CategoryService = Depends(Factory().get_category_service)
):
    category = await service.create(data.dict())
    return category


@router.patch("/categories/{id}", response_model=CategorySchema, dependencies=[Depends(get_current_active_user)])
async def update_category(
    id: UUID7Field,
    data: CategoryUpdateSchema,
    service: CategoryService = Depends(Factory().get_category_service),
):
    category = await service.update(id, data.dict(exclude_unset=True))
    return category


@router.delete(
    "/categories/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def delete_category(id: UUID7Field, service: CategoryService = Depends(Factory().get_category_service)):
    await service.delete(id)
