from app.models import ClassificationModel
from app.repositories import ClassificationRepository

from . import BaseService


class ClassificationService(BaseService[ClassificationModel]):
    def __init__(self, repository: ClassificationRepository):
        super().__init__(ClassificationModel, repository)
        self.repository = repository
