import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _error_response(status_code: int, error: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "detail": detail,
            "status_code": status_code,
        },
    )


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        error_map = {
            400: "bad_request", 401: "unauthorized", 403: "forbidden",
            404: "not_found", 405: "method_not_allowed", 409: "conflict",
            422: "unprocessable_entity", 429: "too_many_requests", 500: "internal_server_error",
        }
        error_type = error_map.get(exc.status_code, "http_error")
        return _error_response(exc.status_code, error_type, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        messages = []
        for err in errors:
            loc = " -> ".join(str(l) for l in err.get("loc", []) if l != "body")
            msg = err.get("msg", "eroare necunoscută")
            messages.append(f"{loc}: {msg}" if loc else msg)
        detail = "; ".join(messages) if messages else "Date invalide în request."
        return _error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, "validation_error", detail)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        return _error_response(status.HTTP_409_CONFLICT, "conflict", "Resursa există deja.")

    @app.exception_handler(OperationalError)
    async def db_operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "database_unavailable", "Baza de date nu este disponibilă.")

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Eroare neașteptată pe %s %s", request.method, request.url.path)
        return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_server_error", "A apărut o eroare internă.")