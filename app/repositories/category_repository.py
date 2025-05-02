from app.models import CategoryModel

from . import BaseRepository


class CategoryRepository(BaseRepository[CategoryModel]):
    def __init__(self, model):
        super().__init__(model)
