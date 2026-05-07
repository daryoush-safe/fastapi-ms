import bcrypt

from src.application.dto import (
    CreateUserDTO,
    DeactivateUserDTO,
    GetUserDTO,
    ResetPasswordDTO,
)
from src.application.use_cases.create_user import CreateUserUseCase
from src.application.use_cases.deactivate_user import DeactivateUserUseCase
from src.application.use_cases.get_user import GetUserUseCase
from src.application.use_cases.reset_password import ResetPasswordUseCase
from src.domain.models import User
from src.domain.ports.unit_of_work import AbstractUnitOfWork


class PasswordHasher:
    def hash(self, plain: str) -> str:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    def verify(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())


class UserService:
    def __init__(self, uow: AbstractUnitOfWork, hasher: PasswordHasher) -> None:
        self._uow = uow
        self._hasher = hasher

    async def get_user(self, dto: GetUserDTO) -> User:
        return await GetUserUseCase(self._uow).execute(dto)

    async def create_user(self, dto: CreateUserDTO) -> User:
        return await CreateUserUseCase(self._uow, self._hasher).execute(dto)

    async def reset_password(self, dto: ResetPasswordDTO) -> None:
        return await ResetPasswordUseCase(self._uow, self._hasher).execute(dto)

    async def deactivate_user(self, dto: DeactivateUserDTO) -> None:
        return await DeactivateUserUseCase(self._uow).execute(dto)
