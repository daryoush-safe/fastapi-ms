from src.application.dto import ResetPasswordDTO
from src.application.services import PasswordHasher
from src.domain.exceptions import UserNotFoundError
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class ResetPasswordUseCase:
    def __init__(self, uow: AbstractUnitOfWork, hasher: PasswordHasher) -> None:
        self._uow = uow
        self._hasher = hasher

    async def execute(self, dto: ResetPasswordDTO) -> None:
        async with self._uow as uow:
            user = await uow.users.get_by_email(dto.email)
            if user is None:
                raise UserNotFoundError(dto.email)

            user.hashed_password = self._hasher.hash(dto.new_password)
            await uow.users.update(user)
