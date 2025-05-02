from app.models import RegionalModel

from . import BaseRepository


class RegionalRepository(BaseRepository[RegionalModel]):
    def __init__(self, model):
        super().__init__(model)
