from dataclasses import dataclass


@dataclass(frozen=True)
class GetUserDTO:
    email: str


@dataclass(frozen=True)
class CreateUserDTO:
    username: str
    email: str
    password: str


@dataclass(frozen=True)
class ResetPasswordDTO:
    email: str
    new_password: str


@dataclass(frozen=True)
class DeactivateUserDTO:
    email: str
