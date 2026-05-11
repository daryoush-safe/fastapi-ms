from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from src.application.password_hasher import PasswordHasher
from src.application.services import UserService
from src.config import Settings, get_settings
from src.infrastructure.persistence.postgres.unit_of_work import SqlAlchemyUnitOfWork


class Container:
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker | None = None
    _user_service: UserService | None = None

    @classmethod
    def _get_settings(cls) -> Settings:
        return get_settings()

    @classmethod
    def _get_session_factory(cls) -> async_sessionmaker:
        if cls._session_factory is None:
            cls._engine = create_async_engine(
                cls._get_settings().database_url,
                echo=cls._get_settings().db_echo,
                pool_size=cls._get_settings().db_pool_size,
                max_overflow=cls._get_settings().db_max_overflow,
            )
            cls._session_factory = async_sessionmaker(
                cls._engine, expire_on_commit=False
            )
        return cls._session_factory

    @classmethod
    def user_service(cls) -> UserService:
        if cls._user_service is None:
            uow = SqlAlchemyUnitOfWork(cls._get_session_factory())
            cls._user_service = UserService(uow=uow, hasher=PasswordHasher())
        return cls._user_service
