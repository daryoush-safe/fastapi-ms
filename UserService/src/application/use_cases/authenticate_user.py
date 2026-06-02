from src.application.dto import AuthenticateUserDTO
from src.application.password_hasher import PasswordHasher
from src.domain.exceptions import InactiveUserError, InvalidCredentialsError
from src.domain.models import User
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class AuthenticateUserUseCase:
    def __init__(self, uow: AbstractUnitOfWork, hasher: PasswordHasher) -> None:
        self._uow = uow
        self._hasher = hasher

    async def execute(self, dto: AuthenticateUserDTO) -> User:
        async with self._uow as uow:
            user = await uow.users.get_by_email(dto.email)
            if user is None or not self._hasher.verify(
                dto.password, user.hashed_password
            ):
                raise InvalidCredentialsError()
            if not user.is_active:
                raise InactiveUserError(user.email)
            return user
