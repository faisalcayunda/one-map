from app.models import MapsetHistoryModel

from . import BaseRepository


class MapsetHistoryRepository(BaseRepository[MapsetHistoryModel]):
    def __init__(self, model):
        super().__init__(model)
