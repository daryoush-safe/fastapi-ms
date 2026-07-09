import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    ConnectionAccessDenied,
    ConnectionNotFound,
    ConnectionVerificationError,
    DomainError,
    InvalidConnectionConfigError,
    QueryExecutionError,
    SQLValidationError,
    UnsupportedEngineError,
)

logger = logging.getLogger(__name__)


def _body(message: str) -> dict:
    return {"detail": message}


def connection_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content=_body(str(exc)))


def connection_access_denied_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=403, content=_body(str(exc)))


def unsupported_engine_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content=_body(str(exc)))


def invalid_connection_config_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content=_body(str(exc)))


def connection_verification_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content=_body(str(exc)))


def sql_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=422, content=_body(str(exc)))


def query_execution_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=422, content=_body(str(exc)))


def unhandled_domain_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled domain error: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content=_body("An unexpected error occurred"))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ConnectionNotFound, connection_not_found_handler)
    app.add_exception_handler(ConnectionAccessDenied, connection_access_denied_handler)
    app.add_exception_handler(UnsupportedEngineError, unsupported_engine_handler)
    app.add_exception_handler(InvalidConnectionConfigError, invalid_connection_config_handler)
    app.add_exception_handler(ConnectionVerificationError, connection_verification_handler)
    app.add_exception_handler(SQLValidationError, sql_validation_handler)
    app.add_exception_handler(QueryExecutionError, query_execution_handler)
    app.add_exception_handler(DomainError, unhandled_domain_handler)
