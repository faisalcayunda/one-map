from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.role_schema import RoleCreateSchema, RoleSchema, RoleUpdateSchema
from app.services import RoleService

router = APIRouter()


@router.get("/roles", response_model=PaginatedResponse[RoleSchema])
async def get_roles(params: CommonParams = Depends(), service: RoleService = Depends(Factory().get_role_service)):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    roles, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[RoleSchema.model_validate(role) for role in roles],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/roles/{id}", response_model=RoleSchema)
async def get_role(id: str, service: RoleService = Depends(Factory().get_role_service)):
    role = await service.find_by_id(id)
    return role


@router.post(
    "/roles",
    response_model=RoleSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_role(data: RoleCreateSchema, service: RoleService = Depends(Factory().get_role_service)):
    role = await service.create(data.dict())
    return role


@router.patch("/roles/{id}", response_model=RoleSchema, dependencies=[Depends(get_current_active_user)])
async def update_role(
    id: str,
    data: RoleUpdateSchema,
    service: RoleService = Depends(Factory().get_role_service),
):
    role = await service.update(id, data.dict(exclude_unset=True))
    return role


@router.delete("/roles/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)])
async def delete_role(id: str, service: RoleService = Depends(Factory().get_role_service)):
    await service.delete(id)
