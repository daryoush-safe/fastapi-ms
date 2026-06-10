from typing import Annotated

from fastapi import Depends
from shared_infra.auth import CurrentUser, make_auth_dependency
from src.application.services import UserService
from src.config import get_settings
from src.container import Container

_settings = get_settings()
_get_current_user = make_auth_dependency(_settings.jwt_secret, _settings.jwt_algorithm)

CurrentUserDep = Annotated[CurrentUser, Depends(_get_current_user)]


def _get_user_service() -> UserService:
    return Container.user_service()


UserServiceDep = Annotated[UserService, Depends(_get_user_service)]
