from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, PydanticCustomError
from pydantic_core.core_schema import (
    is_instance_schema,
    json_or_python_schema,
    no_info_plain_validator_function,
    plain_serializer_function_ser_schema,
    str_schema,
    union_schema,
)
from uuid6 import UUID


class UUID7Field(UUID):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return json_or_python_schema(
            json_schema=str_schema(),
            python_schema=union_schema([is_instance_schema(cls), no_info_plain_validator_function(cls.validate)]),
            serialization=plain_serializer_function_ser_schema(
                lambda x: str(x),
                return_schema=str_schema(),
            ),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except ValueError as e:
            raise PydanticCustomError("uuid_parsing", "Invalid UUID format") from e
