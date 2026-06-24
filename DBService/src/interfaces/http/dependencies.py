from typing import Annotated

from fastapi import Depends
from shared_infra.auth import CurrentUser, make_auth_dependency

from src.application.use_cases.register_connection import RegisterConnectionUseCase
from src.application.use_cases.run_text2sql import RunText2SQL
from src.config import get_settings
from src.container import Container

_settings = get_settings()
_get_current_user = make_auth_dependency(_settings.jwt_secret, _settings.jwt_algorithm)

CurrentUserDep = Annotated[CurrentUser, Depends(_get_current_user)]


def get_run_text2sql() -> RunText2SQL:
    return Container.run_text2sql_use_case()


def get_register_connection() -> RegisterConnectionUseCase:
    return Container.register_connection_use_case()


RunText2SQLDep = Annotated[RunText2SQL, Depends(get_run_text2sql)]
RegisterConnectionDep = Annotated[RegisterConnectionUseCase, Depends(get_register_connection)]
