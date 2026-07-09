import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    DomainError,
    MLServiceError,
    ThreadAccessDenied,
    ThreadNotFound,
)

logger = logging.getLogger(__name__)


def _body(message: str) -> dict:
    return {"detail": message}


def thread_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content=_body(str(exc)))


def thread_access_denied_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=403, content=_body(str(exc)))


def ml_service_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=502, content=_body(str(exc)))


def unhandled_domain_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled domain error: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content=_body("An unexpected error occurred"))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ThreadNotFound, thread_not_found_handler)
    app.add_exception_handler(ThreadAccessDenied, thread_access_denied_handler)
    app.add_exception_handler(MLServiceError, ml_service_handler)
    app.add_exception_handler(DomainError, unhandled_domain_handler)
