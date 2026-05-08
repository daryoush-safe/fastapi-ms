import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.domain.exceptions import (
    PaymentProviderError,
    SecurityValidationError,
    SubscriptionNotFoundError,
)

logger = logging.getLogger(__name__)


def _error_body(message: str) -> dict:
    return {"detail": message}


def subscription_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content=_error_body(str(exc)))


def payment_provider_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=502, content=_error_body(str(exc)))


def security_validation_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content=_error_body(str(exc)))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(SubscriptionNotFoundError, subscription_not_found_handler)
    app.add_exception_handler(PaymentProviderError, payment_provider_error_handler)
    app.add_exception_handler(SecurityValidationError, security_validation_handler)
