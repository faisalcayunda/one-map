from functools import partial

from app.core.minio_client import MinioClient
from app.models import (
    CategoryModel,
    ClassificationModel,
    CredentialModel,
    FileModel,
    MapProjectionSystemModel,
    MapsetHistoryModel,
    MapsetModel,
    MapSourceModel,
    NewsModel,
    OrganizationModel,
    RefreshTokenModel,
    RegionalModel,
    RoleModel,
    UserModel,
)
from app.models.category_model import CategoryModel
from app.repositories import (
    CategoryRepository,
    ClassificationRepository,
    CredentialRepository,
    FileRepository,
    MapProjectionSystemRepository,
    MapsetHistoryRepository,
    MapsetRepository,
    MapSourceRepository,
    NewsRepository,
    OrganizationRepository,
    RegionalRepository,
    RoleRepository,
    TokenRepository,
    UserRepository,
)
from app.services import (
    AuthService,
    CategoryService,
    ClassificationService,
    CredentialService,
    FileService,
    MapProjectionSystemService,
    MapsetHistoryService,
    MapsetService,
    MapSourceService,
    NewsService,
    OrganizationService,
    RegionalService,
    RoleService,
    UserService,
)


class Factory:
    organization_repository = partial(OrganizationRepository, OrganizationModel)
    role_repository = partial(RoleRepository, RoleModel)
    user_repository = partial(UserRepository, UserModel)
    token_repository = partial(TokenRepository, RefreshTokenModel)
    news_repository = partial(NewsRepository, NewsModel)
    file_repository = partial(FileRepository, FileModel)
    credential_repository = partial(CredentialRepository, CredentialModel)
    map_source_repository = partial(MapSourceRepository, MapSourceModel)
    map_projection_system_repository = partial(MapProjectionSystemRepository, MapProjectionSystemModel)
    category_repository = partial(CategoryRepository, CategoryModel)
    classification_repository = partial(ClassificationRepository, ClassificationModel)
    regional_repository = partial(RegionalRepository, RegionalModel)
    mapset_repository = partial(MapsetRepository, MapsetModel)
    mapset_history_repository = partial(MapsetHistoryRepository, MapsetHistoryModel)

    def get_auth_service(
        self,
    ):
        return AuthService(user_repository=self.user_repository(), token_repository=self.token_repository())

    def get_organization_service(
        self,
    ):
        return OrganizationService(self.organization_repository())

    def get_role_service(
        self,
    ):
        return RoleService(self.role_repository())

    def get_user_service(
        self,
    ):
        return UserService(self.user_repository())

    def get_news_service(
        self,
    ):
        return NewsService(self.news_repository())

    def get_file_service(
        self,
    ):
        return FileService(self.file_repository(), MinioClient())

    def get_credential_service(
        self,
    ):
        return CredentialService(self.credential_repository())

    def get_map_source_service(
        self,
    ):
        return MapSourceService(self.map_source_repository())

    def get_map_projection_system_service(
        self,
    ):
        return MapProjectionSystemService(self.map_projection_system_repository())

    def get_category_service(
        self,
    ):
        return CategoryService(self.category_repository())

    def get_classification_service(
        self,
    ):
        return ClassificationService(self.classification_repository())

    def get_regional_service(
        self,
    ):
        return RegionalService(self.regional_repository())

    def get_mapset_service(
        self,
    ):
        return MapsetService(self.mapset_repository(), self.mapset_history_repository())

    def get_mapset_history_service(
        self,
    ):
        return MapsetHistoryService(self.mapset_history_repository())
