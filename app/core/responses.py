from typing import Any, Generic, List, TypeVar

import orjson
from fastapi.responses import JSONResponse

from .serializers import BaseModel


class ORJSONResponse(JSONResponse):
    """Custom JSONResponse menggunakan orjson."""

    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        """Render content menggunakan orjson."""
        return orjson.dumps(
            content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_UUID
        )


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool
