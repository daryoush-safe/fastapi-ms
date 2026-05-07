from typing import Annotated

from fastapi import Depends
from src.application.services import UserService
from src.container import Container


def get_user_service() -> UserService:
    return Container.user_service()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
