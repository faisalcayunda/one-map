from app.models import NewsModel

from . import BaseRepository


class NewsRepository(BaseRepository[NewsModel]):
    def __init__(self, model):
        super().__init__(model)
