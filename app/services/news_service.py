from app.models import NewsModel
from app.repositories import NewsRepository

from . import BaseService


class NewsService(BaseService[NewsModel]):
    def __init__(self, repository: NewsRepository):
        super().__init__(NewsModel, repository)
        self.repository = repository
