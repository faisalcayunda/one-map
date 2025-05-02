from typing import Any

import orjson
from pydantic import BaseModel, ConfigDict


def orjson_dumps(v: Any, *, default=None) -> str:
    """Custom JSON serializer using orjson."""
    return orjson.dumps(
        v,
        default=default,
        option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_UUID | orjson.OPT_UTC_Z,
    ).decode("utf-8")


class ORJSONBaseModel(BaseModel):
    """Base Pydantic model with orjson configuration."""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    def model_dump_json(self, **kwargs):
        """Override default json serialization to use orjson."""
        return orjson.dumps(self.model_dump(**kwargs)).decode("utf-8")
