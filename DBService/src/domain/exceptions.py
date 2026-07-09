import uuid


class DomainError(Exception):
    """Base for all domain errors."""


class ConnectionNotFound(DomainError):
    def __init__(self, connection_id: uuid.UUID) -> None:
        self.connection_id = connection_id
        super().__init__(f"Connection '{connection_id}' not found")


class ConnectionAccessDenied(DomainError):
    def __init__(self, connection_id: uuid.UUID) -> None:
        self.connection_id = connection_id
        super().__init__(f"Not permitted to use connection '{connection_id}'")


class QueryExecutionError(DomainError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Query execution failed: {reason}")


class UnsupportedEngineError(DomainError):
    def __init__(self, engine: str) -> None:
        self.engine = engine
        super().__init__(f"Unsupported database engine: '{engine}'")


class InvalidConnectionConfigError(DomainError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Invalid connection configuration: {reason}")


class ConnectionVerificationError(DomainError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"Could not connect to the target database: {reason}")


class SQLValidationError(DomainError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"SQL validation failed: {reason}")
