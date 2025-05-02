from fastapi import APIRouter

from app.api.v1.routes import (
    auth_router,
    category_router,
    classification_router,
    credential_router,
    file_router,
    map_projection_system_router,
    map_source_router,
    mapset_router,
    news_router,
    organization_router,
    regional_router,
    role_router,
    user_router,
)

router = APIRouter()
router.include_router(auth_router, tags=["Auth"])
router.include_router(category_router, tags=["Categories"])
router.include_router(classification_router, tags=["Classifications"])
router.include_router(credential_router, tags=["Credentials"])
router.include_router(file_router, tags=["Files"])
router.include_router(organization_router, tags=["Organizations"])
router.include_router(mapset_router, tags=["Mapsets"])
router.include_router(map_source_router, tags=["Map Sources"])
router.include_router(map_projection_system_router, tags=["Map Projection Systems"])
router.include_router(news_router, tags=["News"])
router.include_router(regional_router, tags=["Regionals"])
router.include_router(role_router, tags=["Roles"])
router.include_router(user_router, tags=["Users"])
