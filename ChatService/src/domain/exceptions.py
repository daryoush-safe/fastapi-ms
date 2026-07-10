import uuid


class DomainError(Exception):
    """Base for all domain errors."""


class ThreadNotFound(DomainError):
    def __init__(self, thread_id: uuid.UUID) -> None:
        self.thread_id = thread_id
        super().__init__(f"Chat thread '{thread_id}' not found")


class ThreadAccessDenied(DomainError):
    def __init__(self, thread_id: uuid.UUID) -> None:
        self.thread_id = thread_id
        super().__init__(f"Not permitted to access chat thread '{thread_id}'")


class MLServiceError(DomainError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"ML service request failed: {reason}")


class ConnectionNotFound(DomainError):
    def __init__(self, connection_id: uuid.UUID) -> None:
        self.connection_id = connection_id
        super().__init__(f"Database connection '{connection_id}' not found")


class ConnectionAccessDenied(DomainError):
    def __init__(self, connection_id: uuid.UUID) -> None:
        self.connection_id = connection_id
        super().__init__(f"Not permitted to use database connection '{connection_id}'")


class SchemaUnavailable(DomainError):
    def __init__(self, connection_id: uuid.UUID) -> None:
        self.connection_id = connection_id
        super().__init__(
            f"Schema for connection '{connection_id}' is not available yet; try again shortly"
        )


class ConnectionServiceError(DomainError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Connection validation failed: {reason}")
