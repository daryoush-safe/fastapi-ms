class DomainError(Exception):
    """Base for all domain errors."""


class UserNotFoundError(DomainError):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email '{email}' not found")


class UserAlreadyExistsError(DomainError):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("Invalid credentials")


class InactiveUserError(DomainError):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User '{email}' is inactive")
