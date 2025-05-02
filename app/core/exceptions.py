from http import HTTPStatus
from typing import Any, Dict, Optional, Type

from fastapi import status


class APIException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message: str = "Internal server error"

    def __init__(
        self, message: Optional[str] = None, detail: Optional[Any] = None, headers: Optional[Dict[str, str]] = None
    ):
        self.message = message or self.default_message
        self.detail = detail
        self.headers = headers or {}

        super().__init__(self.message)


def create_exception(name: str, status_code: int, default_message: str) -> Type[APIException]:
    return type(name, (APIException,), {"status_code": status_code, "default_message": default_message})


def prepare_error_response(message: str, detail: Any = None, error_type: Optional[str] = None) -> Dict[str, Any]:
    response = {"detail": message}

    if detail is not None:
        if isinstance(detail, dict):
            response.update(detail)
        else:
            response["additional_info"] = detail

    if error_type:
        response["error_type"] = error_type

    return response


BadRequestException = create_exception(
    "BadRequestException", status.HTTP_400_BAD_REQUEST, HTTPStatus.BAD_REQUEST.description
)

NotFoundException = create_exception("NotFoundException", status.HTTP_404_NOT_FOUND, HTTPStatus.NOT_FOUND.description)

ForbiddenException = create_exception(
    "ForbiddenException", status.HTTP_403_FORBIDDEN, HTTPStatus.FORBIDDEN.description
)

UnauthorizedException = create_exception(
    "UnauthorizedException", status.HTTP_401_UNAUTHORIZED, HTTPStatus.UNAUTHORIZED.description
)

UnprocessableEntity = create_exception(
    "UnprocessableEntity", status.HTTP_422_UNPROCESSABLE_ENTITY, HTTPStatus.UNPROCESSABLE_ENTITY.description
)

DuplicateValueException = create_exception(
    "DuplicateValueException", status.HTTP_422_UNPROCESSABLE_ENTITY, HTTPStatus.UNPROCESSABLE_ENTITY.description
)
InvalidInputException = create_exception(
    "InvalidInputException", status.HTTP_422_UNPROCESSABLE_ENTITY, HTTPStatus.UNPROCESSABLE_ENTITY.description
)
