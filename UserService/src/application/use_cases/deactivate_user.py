from src.application.dto import DeactivateUserDTO
from src.domain.exceptions import UserNotFoundError
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class DeactivateUserUseCase:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: DeactivateUserDTO) -> None:
        async with self._uow as uow:
            user = await uow.users.get_by_email(dto.email)
            if user is None:
                raise UserNotFoundError(dto.email)
            user.is_active = False
            await uow.users.update(user)
