from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class NormalizedEntry:
    external_id: str
    transaction_date: date
    amount: Decimal
    description: str
    raw_data: dict = field(default_factory=dict)
