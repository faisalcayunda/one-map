from app.models import MapSourceModel
from app.repositories import MapSourceRepository

from . import BaseService


class MapSourceService(BaseService[MapSourceModel]):
    def __init__(self, repository: MapSourceRepository):
        super().__init__(MapSourceModel, repository)
        self.repository = repository
