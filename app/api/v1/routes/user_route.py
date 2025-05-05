from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.data_types import UUID7Field
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.user_schema import UserCreateSchema, UserSchema, UserUpdateSchema
from app.services import UserService

router = APIRouter()


@router.get("/users", response_model=PaginatedResponse[UserSchema])
async def get_users(params: CommonParams = Depends(), service: UserService = Depends(Factory().get_user_service)):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    users, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[UserSchema.model_validate(user) for user in users],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/users/{id}", response_model=UserSchema)
async def get_user(id: UUID7Field, service: UserService = Depends(Factory().get_user_service)):
    user = await service.find_by_id(id)
    return user


@router.post(
    "/users",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_user(data: UserCreateSchema, service: UserService = Depends(Factory().get_user_service)):
    user = await service.create(data.dict())
    return user


@router.patch("/users/{id}", response_model=UserSchema, dependencies=[Depends(get_current_active_user)])
async def update_user(
    id: UUID7Field,
    data: UserUpdateSchema,
    service: UserService = Depends(Factory().get_user_service),
):
    user = await service.update(id, data.dict(exclude_unset=True))
    return user


@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)])
async def delete_user(id: UUID7Field, service: UserService = Depends(Factory().get_user_service)):
    await service.delete(id)
