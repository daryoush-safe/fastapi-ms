from fastapi import APIRouter

from DBService.src.application.dto import RunText2SQLCommand
from DBService.src.interfaces.http.dependencies import RunText2SQLDep
from DBService.src.interfaces.http.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse, status_code=200)
async def run_query(
    request: QueryRequest,
    use_case: RunText2SQLDep,
) -> QueryResponse:
    result = await use_case.execute(
        RunText2SQLCommand(
            connection_id=request.connection_id,
            prompt=request.prompt,
        )
    )
    return QueryResponse(
        generated_sql=result.generated_sql,
        columns=result.columns,
        rows=result.rows,
    )
