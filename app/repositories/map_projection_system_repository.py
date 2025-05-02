from app.models import MapProjectionSystemModel

from . import BaseRepository


class MapProjectionSystemRepository(BaseRepository[MapProjectionSystemModel]):
    def __init__(self, model):
        super().__init__(model)
