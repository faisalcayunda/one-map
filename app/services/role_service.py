from app.models import RoleModel
from app.repositories import RoleRepository

from . import BaseService


class RoleService(BaseService[RoleModel]):
    def __init__(self, repository: RoleRepository):
        super().__init__(RoleModel, repository)
        self.repository = repository
