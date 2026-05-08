from uuid import UUID


class DomainError(Exception):
    """Base for all domain errors."""


class SubscriptionNotFoundError(DomainError):
    def __init__(self, id: UUID) -> None:
        self.id = id
        super().__init__(f"Subscription with ID '{id}' not found")


class PaymentProviderError(DomainError):
    def __init__(self) -> None:
        super().__init__("Payment provider not working")


class SecurityValidationError(DomainError):
    def __init__(self) -> None:
        super().__init__("External request fails security verification")
