from app.models import SourceUsageModel

from . import BaseRepository


class SourceUsageRepository(BaseRepository[SourceUsageModel]):
    def __init__(self, model):
        super().__init__(model)
