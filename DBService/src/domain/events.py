import uuid
from dataclasses import dataclass, field

from shared_core.base_event import DomainEvent


@dataclass(frozen=True)
class QueryExecuted(DomainEvent):
    connection_id: uuid.UUID = field(default_factory=uuid.uuid4)
    prompt: str = ""
    generated_sql: str = ""
