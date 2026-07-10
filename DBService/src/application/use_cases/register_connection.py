import uuid

from src.application.dto import RegisterConnectionDTO
from src.domain.exceptions import (
    ConnectionVerificationError,
    InvalidConnectionConfigError,
    UnsupportedEngineError,
)
from src.domain.models import DatabaseConnection
from src.domain.ports.connection_verifier import IConnectionVerifier
from src.domain.ports.unit_of_work import IUnitOfWork
from src.domain.value_objects import build_dsn, is_supported_engine


class RegisterConnectionUseCase:
    def __init__(self, uow: IUnitOfWork, verifier: IConnectionVerifier) -> None:
        self._uow = uow
        self._verifier = verifier

    async def execute(self, dto: RegisterConnectionDTO) -> DatabaseConnection:
        engine = dto.engine.lower()
        if not is_supported_engine(engine):
            raise UnsupportedEngineError(dto.engine)

        dsn = self._resolve_dsn(engine, dto)

        try:
            await self._verifier.verify(engine, dsn)
        except Exception as e:
            raise ConnectionVerificationError(str(e)) from e

        conn = DatabaseConnection(
            id=uuid.uuid4(),
            owner_id=dto.owner_id,
            name=dto.name,
            engine=engine,
            dsn=dsn,
            schema_cache=None,
            is_active=True,
        )
        conn.record_registered()
        async with self._uow as uow:
            await uow.connections.add(conn)
        return conn

    @staticmethod
    def _resolve_dsn(engine: str, dto: RegisterConnectionDTO) -> str:
        if dto.dsn:
            return dto.dsn
        try:
            return build_dsn(
                engine,
                host=dto.host,
                port=dto.port,
                username=dto.username,
                password=dto.password,
                database=dto.database,
            )
        except ValueError as e:
            raise InvalidConnectionConfigError(str(e)) from e
