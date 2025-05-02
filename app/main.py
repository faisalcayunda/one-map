from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware

from app.api.v1 import router as api_router
from app.core.config import settings
from app.core.exceptions import APIException, prepare_error_response

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=settings.DATABASE_URL,
    engine_args={"echo": settings.DEBUG},
)
app.add_middleware(
    BrotliMiddleware,
    minimum_size=1000,
)

app.include_router(api_router)


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    response_content = prepare_error_response(message=exc.message)

    return JSONResponse(status_code=exc.status_code, content=response_content, headers=exc.headers)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response_content = prepare_error_response(message=str(exc.detail))

    return JSONResponse(status_code=exc.status_code, content=response_content, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response_content = prepare_error_response(
        message="Validation error",
        detail=exc.errors(),
    )

    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response_content)


@app.exception_handler(LookupError)
async def enum_exception_handler(request: Request, exc: LookupError):
    error_message = str(exc)

    if "is not among the defined enum values" in error_message:
        response_content = prepare_error_response(
            message="Invalid enum value",
            detail=error_message,
        )
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response_content)

    raise exc


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    response_content = prepare_error_response(
        message="Internal server error", detail=str(exc) if settings.DEBUG else None
    )

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_content)
