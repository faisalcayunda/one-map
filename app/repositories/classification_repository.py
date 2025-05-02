from app.models import ClassificationModel

from . import BaseRepository


class ClassificationRepository(BaseRepository[ClassificationModel]):
    def __init__(self, model):
        super().__init__(model)
