import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.domain.exceptions import (
    DomainError,
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


def _error_body(message: str) -> dict:
    return {"detail": message}


def user_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content=_error_body(str(exc)))


def user_already_exists_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=409, content=_error_body(str(exc)))


def invalid_credentials_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=401, content=_error_body(str(exc)))


def inactive_user_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=403, content=_error_body(str(exc)))


def unhandled_domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled domain error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500, content=_error_body("An unexpected error occurred")
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
    app.add_exception_handler(InactiveUserError, inactive_user_handler)
    app.add_exception_handler(DomainError, unhandled_domain_error_handler)
