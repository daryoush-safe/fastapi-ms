from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from shared_infra.auth import CurrentUser, make_auth_dependency

from src.application.services import ChatService
from src.config import get_settings
from src.container import Container

_settings = get_settings()
_get_current_user = make_auth_dependency(_settings.jwt_secret, _settings.jwt_algorithm)
_bearer = HTTPBearer(auto_error=True)

CurrentUserDep = Annotated[CurrentUser, Depends(_get_current_user)]


def get_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> str:
    return credentials.credentials


AccessTokenDep = Annotated[str, Depends(get_access_token)]


def get_chat_service() -> ChatService:
    return Container.chat_service()


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
