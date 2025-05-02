from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas import (
    ClassificationCreateSchema,
    ClassificationSchema,
    ClassificationUpdateSchema,
)
from app.services import ClassificationService

router = APIRouter()


@router.get("/classifications", response_model=PaginatedResponse[ClassificationSchema])
async def get_classifications(
    params: CommonParams = Depends(), service: ClassificationService = Depends(Factory().get_classification_service)
):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    classifications, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[ClassificationSchema.model_validate(classification) for classification in classifications],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/classifications/{id}", response_model=ClassificationSchema)
async def get_classification(id: str, service: ClassificationService = Depends(Factory().get_classification_service)):
    classification = await service.find_by_id(id)
    return classification


@router.post(
    "/classifications",
    response_model=ClassificationSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_classification(
    data: ClassificationCreateSchema, service: ClassificationService = Depends(Factory().get_classification_service)
):
    classification = await service.create(data.dict())
    return classification


@router.patch(
    "/classifications/{id}", response_model=ClassificationSchema, dependencies=[Depends(get_current_active_user)]
)
async def update_classification(
    id: str,
    data: ClassificationUpdateSchema,
    service: ClassificationService = Depends(Factory().get_classification_service),
):
    classification = await service.update(id, data.dict(exclude_unset=True))
    return classification


@router.delete(
    "/classifications/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def delete_classification(
    id: str, service: ClassificationService = Depends(Factory().get_classification_service)
):
    await service.delete(id)
