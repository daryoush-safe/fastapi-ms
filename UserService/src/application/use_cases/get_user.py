from src.application.dto import GetUserDTO
from src.domain.exceptions import UserNotFoundError
from src.domain.models import User
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class GetUserUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: GetUserDTO) -> User:
        async with self._uow as uow:
            user = await uow.users.get_by_email(dto.email)
            if user is None:
                raise UserNotFoundError(dto.email)
            return user
