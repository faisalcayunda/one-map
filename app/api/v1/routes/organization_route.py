from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_active_user, get_payload
from app.api.dependencies.factory import Factory
from app.core.data_types import UUID7Field
from app.core.params import CommonParams
from app.core.responses import PaginatedResponse
from app.schemas.organization_schema import (
    OrganizationCreateSchema,
    OrganizationSchema,
    OrganizationUpdateSchema,
)
from app.schemas.user_schema import UserSchema
from app.services import OrganizationService

router = APIRouter()


@router.get("/organizations", response_model=PaginatedResponse[OrganizationSchema])
async def get_organizations(
    params: CommonParams = Depends(),
    user: UserSchema = Depends(get_payload),
    service: OrganizationService = Depends(Factory().get_organization_service),
):
    filter = params.filter
    sort = params.sort
    search = params.search
    group_by = params.group_by
    limit = params.limit
    offset = params.offset
    organizations, total = await service.find_all(user, filter, sort, search, group_by, limit, offset)

    return PaginatedResponse(
        items=[OrganizationSchema.model_validate(organization) for organization in organizations],
        total=total,
        limit=limit,
        offset=offset,
        has_more=total > (offset + limit),
    )


@router.get("/organizations/{id}", response_model=OrganizationSchema)
async def get_organization(id: UUID7Field, service: OrganizationService = Depends(Factory().get_organization_service)):
    organization = await service.get_organizations_by_id(id)
    return organization


@router.post(
    "/organizations",
    response_model=OrganizationSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)],
)
async def create_organization(
    data: OrganizationCreateSchema, service: OrganizationService = Depends(Factory().get_organization_service)
):
    organization = await service.create(data.dict())
    return organization


@router.patch(
    "/organizations/{id}", response_model=OrganizationSchema, dependencies=[Depends(get_current_active_user)]
)
async def update_organization(
    id: UUID7Field,
    data: OrganizationUpdateSchema,
    service: OrganizationService = Depends(Factory().get_organization_service),
):
    organization = await service.update(id, data.dict(exclude_unset=True))
    return organization


@router.delete(
    "/organizations/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_active_user)]
)
async def delete_organization(
    id: UUID7Field, service: OrganizationService = Depends(Factory().get_organization_service)
):
    await service.delete(id)
