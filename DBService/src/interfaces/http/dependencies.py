from typing import Annotated

from fastapi import Depends

from DBService.src.application.use_cases.register_connection import RegisterConnectionUseCase
from DBService.src.application.use_cases.run_text2sql import RunText2SQL
from DBService.src.container import Container


def get_run_text2sql() -> RunText2SQL:
    return Container.run_text2sql_use_case()


def get_register_connection() -> RegisterConnectionUseCase:
    return Container.register_connection_use_case()


RunText2SQLDep = Annotated[RunText2SQL, Depends(get_run_text2sql)]
RegisterConnectionDep = Annotated[RegisterConnectionUseCase, Depends(get_register_connection)]
