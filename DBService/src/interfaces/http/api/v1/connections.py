from fastapi import APIRouter

from DBService.src.application.dto import RegisterConnectionCommand
from DBService.src.interfaces.http.dependencies import RegisterConnectionDep
from DBService.src.interfaces.http.schemas import ConnectionResponse, RegisterConnectionRequest

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("", response_model=ConnectionResponse, status_code=201)
async def register_connection(
    request: RegisterConnectionRequest,
    use_case: RegisterConnectionDep,
) -> ConnectionResponse:
    conn = await use_case.execute(
        RegisterConnectionCommand(
            owner_id=request.owner_id,
            name=request.name,
            engine=request.engine,
            dsn=request.dsn,
        )
    )
    return ConnectionResponse(
        id=conn.id, name=conn.name, engine=conn.engine, is_active=conn.is_active
    )
