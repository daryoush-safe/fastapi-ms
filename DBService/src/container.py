from collections.abc import Callable

from shared_infra.metrics import instrument_db_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.application.services import DBService
from src.config import Settings, get_settings
from src.domain.ports.unit_of_work import IUnitOfWork
from src.infrastructure.connection_probe.sqlalchemy_verifier import (
    SqlAlchemyConnectionVerifier,
)
from src.infrastructure.persistence.postgres.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.query_execution.sqlalchemy_executor import SqlAlchemyQueryExecutor
from src.infrastructure.schema_extraction.sqlalchemy_extractor import (
    SqlAlchemySchemaExtractor,
)


class Container:
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None
    _db_service: DBService | None = None

    @classmethod
    def _settings(cls) -> Settings:
        return get_settings()

    @classmethod
    def _get_session_factory(cls) -> async_sessionmaker[AsyncSession]:
        if cls._session_factory is None:
            s = cls._settings()
            cls._engine = create_async_engine(
                s.database_url,
                echo=s.db_echo,
                pool_size=s.db_pool_size,
                max_overflow=s.db_max_overflow,
            )
            cls._session_factory = async_sessionmaker(cls._engine, expire_on_commit=False)
            instrument_db_engine(cls._engine)
        return cls._session_factory

    @classmethod
    def engine(cls) -> AsyncEngine:
        cls._get_session_factory()
        assert cls._engine is not None
        return cls._engine

    @classmethod
    def _uow_factory(cls) -> Callable[[], IUnitOfWork]:
        session_factory = cls._get_session_factory()
        return lambda: SqlAlchemyUnitOfWork(session_factory)

    @classmethod
    def db_service(cls) -> DBService:
        if cls._db_service is None:
            cls._db_service = DBService(
                uow_factory=cls._uow_factory(),
                connection_verifier=SqlAlchemyConnectionVerifier(),
                query_executor=SqlAlchemyQueryExecutor(),
                schema_extractor=SqlAlchemySchemaExtractor(),
            )
        return cls._db_service
