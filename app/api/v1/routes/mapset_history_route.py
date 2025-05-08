from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.data_types import UUID7Field
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas import MapsetHistoryCreateSchema, MapsetHistorySchema
from app.schemas.user_schema import UserSchema
from app.services import MapsetHistoryService

router = APIRouter()


@router.get(
    "/histories",
    response_model=PaginatedResponse[MapsetHistorySchema],
    dependencies=[Depends(get_current_active_user)],
)
async def get_mapset_histories(
    params: CommonParams = Depends(), service: MapsetHistoryService = Depends(Factory().get_mapset_history_service)
):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    histories, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[MapsetHistorySchema.model_validate(history) for history in histories],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.post("/histories", response_model=MapsetHistorySchema, status_code=status.HTTP_201_CREATED)
async def record_history(
    data: MapsetHistoryCreateSchema,
    user: UserSchema = Depends(get_current_active_user),
    service: MapsetHistoryService = Depends(Factory().get_mapset_history_service),
):
    return await service.create(user, data.dict())


@router.delete(
    "/histories/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def delete_history(
    id: UUID7Field, service: MapsetHistoryService = Depends(Factory().get_mapset_history_service)
):
    await service.delete(id)
