import uuid

from src.application.dto import RegisterConnectionCommand
from src.domain.exceptions import UnsupportedEngineError
from src.domain.models import DatabaseConnection
from src.domain.ports.unit_of_work import IUnitOfWork

_SUPPORTED_ENGINES = {"postgres", "mysql", "sqlite"}


class RegisterConnectionUseCase:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, cmd: RegisterConnectionCommand) -> DatabaseConnection:
        if cmd.engine not in _SUPPORTED_ENGINES:
            raise UnsupportedEngineError(cmd.engine)

        conn = DatabaseConnection(
            id=uuid.uuid4(),
            owner_id=cmd.owner_id,
            name=cmd.name,
            engine=cmd.engine,
            dsn=cmd.dsn,
            schema_cache=None,
            is_active=True,
        )
        async with self._uow as uow:
            await uow.connections.add(conn)
        return conn
