from src.application.dto import CreateUserDTO
from src.application.services import PasswordHasher
from src.domain.exceptions import UserAlreadyExistsError
from src.domain.models import User
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class CreateUserUseCase:
    def __init__(self, uow: AbstractUnitOfWork, hasher: PasswordHasher) -> None:
        self._uow = uow
        self._hasher = hasher

    async def execute(self, dto: CreateUserDTO) -> User:
        async with self._uow as uow:
            if await uow.users.exists_by_email(dto.email):
                raise UserAlreadyExistsError(dto.email)

            user = User.create(
                username=dto.username,
                email=dto.email,
                hashed_password=self._hasher.hash(dto.password),
            )
            await uow.users.add(user)
            return user
