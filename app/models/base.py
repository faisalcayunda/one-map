from typing import Any, Dict

from sqlalchemy.orm import declarative_base


class Base(declarative_base()):
    __abstract__ = True

    def to_dict(self, exclude: dict = {}) -> Dict["str", Any]:
        if self is None:
            return {}
        return {col.name: getattr(self, col.name) for col in self.__table__.columns if col.name not in exclude}
