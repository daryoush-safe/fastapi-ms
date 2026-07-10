import uuid

from fastapi import APIRouter, BackgroundTasks
from src.application.dto import (
    ExtractSchemaDTO,
    GetConnectionDTO,
    ListConnectionsDTO,
    RegisterConnectionDTO,
)
from src.interfaces.http.dependencies import CurrentUserDep, DBServiceDep
from src.interfaces.http.schemas import (
    ConnectionResponse,
    ExtractSchemaResponse,
    RegisterConnectionRequest,
)

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("", response_model=ConnectionResponse, status_code=201)
async def register_connection(
    request: RegisterConnectionRequest,
    service: DBServiceDep,
    current: CurrentUserDep,
    background_tasks: BackgroundTasks,
) -> ConnectionResponse:
    conn = await service.register_connection(
        RegisterConnectionDTO(
            owner_id=uuid.UUID(current.user_id),
            name=request.name,
            engine=request.engine,
            dsn=request.dsn,
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password,
            database=request.database,
        )
    )
    background_tasks.add_task(
        service.refresh_schema,
        ExtractSchemaDTO(connection_id=conn.id, owner_id=conn.owner_id),
    )
    return ConnectionResponse(
        id=conn.id, name=conn.name, engine=conn.engine, is_active=conn.is_active
    )


@router.get("", response_model=list[ConnectionResponse], status_code=200)
async def list_connections(
    service: DBServiceDep,
    current: CurrentUserDep,
) -> list[ConnectionResponse]:
    conns = await service.list_connections(ListConnectionsDTO(owner_id=uuid.UUID(current.user_id)))
    return [
        ConnectionResponse(id=c.id, name=c.name, engine=c.engine, is_active=c.is_active)
        for c in conns
    ]


@router.get("/{connection_id}", response_model=ConnectionResponse, status_code=200)
async def get_connection(
    connection_id: uuid.UUID,
    service: DBServiceDep,
    current: CurrentUserDep,
) -> ConnectionResponse:
    conn = await service.get_connection(
        GetConnectionDTO(
            connection_id=connection_id,
            owner_id=uuid.UUID(current.user_id),
        )
    )
    return ConnectionResponse(
        id=conn.id, name=conn.name, engine=conn.engine, is_active=conn.is_active
    )


@router.get("/{connection_id}/schema", response_model=ExtractSchemaResponse, status_code=200)
async def extract_schema(
    connection_id: uuid.UUID,
    service: DBServiceDep,
    current: CurrentUserDep,
) -> ExtractSchemaResponse:
    result = await service.extract_schema(
        ExtractSchemaDTO(
            connection_id=connection_id,
            owner_id=uuid.UUID(current.user_id),
        )
    )
    return ExtractSchemaResponse.model_validate(result)
