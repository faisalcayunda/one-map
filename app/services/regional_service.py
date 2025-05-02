from app.models import RegionalModel
from app.repositories import RegionalRepository

from . import BaseService


class RegionalService(BaseService[RegionalModel]):
    def __init__(self, repository: RegionalRepository):
        super().__init__(RegionalModel, repository)
        self.repository = repository
