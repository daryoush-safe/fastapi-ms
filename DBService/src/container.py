import httpx
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from DBService.src.application.use_cases.register_connection import RegisterConnectionUseCase
from DBService.src.application.use_cases.run_text2sql import RunText2SQL
from DBService.src.config import Settings, get_settings
from DBService.src.domain.ports.unit_of_work import IUnitOfWork
from DBService.src.infrastructure.db_introspection.sqlalchemy_schema_reader import (
    SqlAlchemySchemaReader,
)
from DBService.src.infrastructure.messaging.outbox_publisher import OutboxPublisher
from DBService.src.infrastructure.persistence.postgres.unit_of_work import SqlAlchemyUnitOfWork
from DBService.src.infrastructure.query_execution.sqlalchemy_executor import SqlAlchemyQueryExecutor
from DBService.src.infrastructure.sql_generation.pruner_generator import PrunerSQLGenerator


class Container:
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None
    _http_client: httpx.AsyncClient | None = None

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
        return cls._session_factory

    @classmethod
    def engine(cls) -> AsyncEngine:
        cls._get_session_factory()
        assert cls._engine is not None
        return cls._engine

    @classmethod
    def _get_http_client(cls) -> httpx.AsyncClient:
        if cls._http_client is None:
            raise RuntimeError("HTTP client not initialised — call Container.startup() first")
        return cls._http_client

    @classmethod
    async def startup(cls) -> None:
        cls._http_client = httpx.AsyncClient(timeout=cls._settings().pruner_timeout)

    @classmethod
    async def shutdown(cls) -> None:
        if cls._http_client is not None:
            await cls._http_client.aclose()
            cls._http_client = None

    @classmethod
    def _new_uow(cls) -> IUnitOfWork:
        return SqlAlchemyUnitOfWork(cls._get_session_factory())

    @classmethod
    def run_text2sql_use_case(cls) -> RunText2SQL:
        s = cls._settings()
        return RunText2SQL(
            uow=cls._new_uow(),
            schema_reader=SqlAlchemySchemaReader(),
            sql_generator=PrunerSQLGenerator(
                base_url=s.pruner_base_url,
                client=cls._get_http_client(),
            ),
            query_executor=SqlAlchemyQueryExecutor(),
            publisher=OutboxPublisher(cls._get_session_factory()),
        )

    @classmethod
    def register_connection_use_case(cls) -> RegisterConnectionUseCase:
        return RegisterConnectionUseCase(uow=cls._new_uow())
