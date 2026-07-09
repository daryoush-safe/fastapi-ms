import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.application.dto import (
    CreateThreadDTO,
    GetMessagesDTO,
    ListThreadsDTO,
    SendMessageDTO,
)
from src.interfaces.http.dependencies import ChatServiceDep, CurrentUserDep
from src.interfaces.http.schemas import (
    CreateThreadRequest,
    MessageResponse,
    SendMessageRequest,
    ThreadResponse,
)

router = APIRouter(prefix="/threads", tags=["threads"])


@router.post("", response_model=ThreadResponse, status_code=201)
async def create_thread(
    request: CreateThreadRequest,
    service: ChatServiceDep,
    current: CurrentUserDep,
) -> ThreadResponse:
    thread = await service.create_thread(
        CreateThreadDTO(user_id=uuid.UUID(current.user_id), title=request.title)
    )
    return ThreadResponse.model_validate(thread)


@router.get("", response_model=list[ThreadResponse])
async def list_threads(
    service: ChatServiceDep,
    current: CurrentUserDep,
) -> list[ThreadResponse]:
    threads = await service.list_threads(ListThreadsDTO(user_id=uuid.UUID(current.user_id)))
    return [ThreadResponse.model_validate(thread) for thread in threads]


@router.get("/{thread_id}/messages", response_model=list[MessageResponse])
async def get_thread_messages(
    thread_id: uuid.UUID,
    service: ChatServiceDep,
    current: CurrentUserDep,
) -> list[MessageResponse]:
    messages = await service.get_thread_messages(
        GetMessagesDTO(thread_id=thread_id, user_id=uuid.UUID(current.user_id))
    )
    return [MessageResponse.model_validate(message) for message in messages]


@router.post("/{thread_id}/messages")
async def send_message(
    thread_id: uuid.UUID,
    request: SendMessageRequest,
    service: ChatServiceDep,
    current: CurrentUserDep,
) -> StreamingResponse:
    stream = await service.send_message(
        SendMessageDTO(
            thread_id=thread_id,
            user_id=uuid.UUID(current.user_id),
            question=request.question,
            schema=request.schema_text,
        )
    )
    return StreamingResponse(stream, media_type="text/event-stream")
