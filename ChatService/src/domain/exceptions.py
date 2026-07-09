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
