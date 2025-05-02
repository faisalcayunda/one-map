from app.models import CategoryModel
from app.repositories import CategoryRepository

from . import BaseService


class CategoryService(BaseService[CategoryModel]):
    def __init__(self, repository: CategoryRepository):
        super().__init__(CategoryModel, repository)
        self.repository = repository
