from typing import List

from fastapi import APIRouter, Body, Depends, status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.factory import Factory
from app.core.data_types import UUID7Field
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.news_schema import NewsCreateSchema, NewsSchema, NewsUpdateSchema
from app.services import NewsService

router = APIRouter()


@router.get("/news", response_model=PaginatedResponse[NewsSchema])
async def get_newss(params: CommonParams = Depends(), service: NewsService = Depends(Factory().get_news_service)):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    newss, total = await service.find_all(filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[NewsSchema.model_validate(news) for news in newss],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/news/{id}", response_model=NewsSchema)
async def get_news(id: UUID7Field, service: NewsService = Depends(Factory().get_news_service)):
    news = await service.find_by_id(id)
    return news


@router.post(
    "/news",
    response_model=NewsSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_news(data: NewsCreateSchema, service: NewsService = Depends(Factory().get_news_service)):
    news = await service.create(data.dict())
    return news


@router.patch(
    "/news/activation", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def update_news_activation(
    ids: List[UUID7Field] = Body(...),
    is_active: bool = Body(...),
    service: NewsService = Depends(Factory().get_news_service),
):
    await service.bulk_update_activation(ids, is_active)


@router.patch("/news/{id}", response_model=NewsSchema, dependencies=[Depends(get_current_active_user)])
async def update_news(
    id: UUID7Field,
    data: NewsUpdateSchema,
    service: NewsService = Depends(Factory().get_news_service),
):
    news = await service.update(id, data.dict(exclude_unset=True))
    return news


@router.delete("/news/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)])
async def delete_news(id: UUID7Field, service: NewsService = Depends(Factory().get_news_service)):
    await service.delete(id)
