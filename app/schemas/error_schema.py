from app.core.serializers import ORJSONBaseModel


class ErrorResponse(ORJSONBaseModel):
    message: str
