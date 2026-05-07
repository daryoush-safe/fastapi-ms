from typing import Annotated

from fastapi import APIRouter, Query
from src.application.dto import (
    CreateUserDTO,
    DeactivateUserDTO,
    GetUserDTO,
    ResetPasswordDTO,
)
from src.interfaces.http.dependencies import UserServiceDep
from src.interfaces.http.schemas import (
    CreateUserRequest,
    DeactivateUserRequest,
    GetUserRequest,
    ResetPasswordRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


def _to_user_response(user) -> UserResponse:
    return UserResponse(
        username=user.username,
        email=user.email,
        is_active=user.is_active,
    )


@router.get("", response_model=UserResponse, status_code=200)
async def get_user(
    request: Annotated[GetUserRequest, Query()],
    user_service: UserServiceDep,
) -> UserResponse:
    user = await user_service.get_user(GetUserDTO(email=request.email))
    return _to_user_response(user)


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    request: CreateUserRequest,
    user_service: UserServiceDep,
) -> UserResponse:
    user = await user_service.create_user(
        CreateUserDTO(
            username=request.username,
            email=request.email,
            password=request.password,
        )
    )
    return _to_user_response(user)


@router.put("/reset-password", status_code=204)
async def reset_password(
    request: ResetPasswordRequest,
    user_service: UserServiceDep,
) -> None:
    await user_service.reset_password(
        ResetPasswordDTO(email=request.email, new_password=request.password)
    )


@router.put("/deactivate", status_code=204)
async def deactivate_user(
    request: Annotated[DeactivateUserRequest, Query()],
    user_service: UserServiceDep,
) -> None:
    await user_service.deactivate_user(DeactivateUserDTO(email=request.email))
