from app.models import RoleModel

from . import BaseRepository


class RoleRepository(BaseRepository[RoleModel]):
    def __init__(self, model):
        super().__init__(model)
