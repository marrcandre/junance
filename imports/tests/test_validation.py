from datetime import date
from decimal import Decimal

from imports.adapters.base import NormalizedEntry
from imports.validators import validate_entries


def test_validation_rejects_duplicate_external_ids_and_invalid_dates():
    entries = [
        NormalizedEntry("same", date(2026, 1, 1), Decimal("10.00"), "A"),
        NormalizedEntry("same", date(2026, 1, 1), Decimal("12.00"), "B"),
    ]

    errors = validate_entries(entries)

    assert "duplicado" in " ".join(errors).lower()


def test_validation_accepts_decimal_values_and_signs():
    entries = [NormalizedEntry("one", date(2026, 1, 1), Decimal("-10.00"), "Compra")]

    assert validate_entries(entries) == []
