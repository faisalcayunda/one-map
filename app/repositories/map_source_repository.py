from app.models import MapSourceModel

from . import BaseRepository


class MapSourceRepository(BaseRepository[MapSourceModel]):
    def __init__(self, model):
        super().__init__(model)
