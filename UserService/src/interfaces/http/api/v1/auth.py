from fastapi import APIRouter
from shared_core.security import create_access_token
from src.application.dto import AuthenticateUserDTO
from src.config import get_settings
from src.interfaces.http.dependencies import UserServiceDep
from src.interfaces.http.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(
    request: LoginRequest,
    user_service: UserServiceDep,
) -> TokenResponse:
    # Authenticate against the user store, then mint a token in the interface layer
    # (the application/domain layers stay free of JWT concerns). Invalid credentials
    # / inactive user raise domain errors mapped to 401 / 403 by the exception handlers.
    user = await user_service.authenticate(
        AuthenticateUserDTO(email=request.email, password=request.password)
    )
    token = create_access_token(
        subject=str(user.id),
        email=user.email,
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        expires_minutes=settings.jwt_access_token_expire_minutes,
    )
    return TokenResponse(access_token=token)
