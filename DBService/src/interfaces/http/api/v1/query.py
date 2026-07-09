import uuid

from fastapi import APIRouter
from src.application.dto import RunText2SQLDTO
from src.interfaces.http.dependencies import CurrentUserDep, DBServiceDep
from src.interfaces.http.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse, status_code=200)
async def run_query(
    request: QueryRequest,
    service: DBServiceDep,
    current: CurrentUserDep,
) -> QueryResponse:
    result = await service.run_text2sql(
        RunText2SQLDTO(
            connection_id=request.connection_id,
            owner_id=uuid.UUID(current.user_id),
            sql=request.sql,
        )
    )
    return QueryResponse(columns=result.columns, rows=result.rows)
