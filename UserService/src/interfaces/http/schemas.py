from pydantic import BaseModel, EmailStr, Field, model_validator
from typing_extensions import Self


class GetUserRequest(BaseModel):
    email: EmailStr


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    password_repeat: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("Passwords do not match")
        return self


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    password_repeat: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("Passwords do not match")
        return self


class DeactivateUserRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    username: str
    email: str
    is_active: bool

    model_config = {"from_attributes": True}
