from .auth_route import router as auth_router
from .category_route import router as category_router
from .classification_route import router as classification_router
from .credential_route import router as credential_router
from .file_route import router as file_router
from .map_projection_system_route import router as map_projection_system_router
from .map_source_route import router as map_source_router
from .mapset_history_route import router as mapset_history_router
from .mapset_route import router as mapset_router
from .news_route import router as news_router
from .organization_route import router as organization_router
from .regional_route import router as regional_router
from .role_route import router as role_router
from .user_route import router as user_router

__all__ = [
    "organization_router",
    "role_router",
    "user_router",
    "auth_router",
    "news_router",
    "file_router",
    "credential_router",
    "map_source_router",
    "map_projection_system_router",
    "category_router",
    "regional_router",
    "mapset_router",
    "classification_router",
    "mapset_history_router",
]
