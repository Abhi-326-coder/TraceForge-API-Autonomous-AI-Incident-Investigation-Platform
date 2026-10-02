from dataclasses import dataclass


@dataclass
class Incident:
    id: str
    title: str
    description: str
    service: str
    severity: str
    status: str


CHECKOUT_DATABASE_INCIDENT = Incident(
    id="INC-001",
    title="Checkout API returning HTTP 500 errors",
    description=(
        "Customers are unable to complete checkout. "
        "The checkout API has started returning HTTP 500 errors."
    ),
    service="checkout-api",
    severity="HIGH",
    status="OPEN",
)