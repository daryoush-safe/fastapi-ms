from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.application.services import SubscriptionService
from src.config import Settings, get_settings
from src.infrastructure.persistence.postgres.unit_of_work import SqlAlchemyUnitOfWork


class Container:
    _subscription_service: SubscriptionService | None = None

    @classmethod
    def _get_settings(cls) -> Settings:
        return get_settings()

    @classmethod
    def _get_session_factory(cls) -> async_sessionmaker:
        settings = cls._get_settings()
        engine = create_async_engine(
            settings.database_url,
            echo=settings.db_echo,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
        )
        return async_sessionmaker(engine, expire_on_commit=False)

    @classmethod
    def subscription_service(cls) -> SubscriptionService:
        if cls._subscription_service is None:
            session_factory = cls._get_session_factory()
            uow = SqlAlchemyUnitOfWork(session_factory)
            cls._subscription_service = SubscriptionService(uow=uow)
        return cls._subscription_service
