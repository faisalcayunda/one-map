from app.models import MapProjectionSystemModel
from app.repositories import MapProjectionSystemRepository

from . import BaseService


class MapProjectionSystemService(BaseService[MapProjectionSystemModel]):
    def __init__(self, repository: MapProjectionSystemRepository):
        super().__init__(MapProjectionSystemModel, repository)
        self.repository = repository
