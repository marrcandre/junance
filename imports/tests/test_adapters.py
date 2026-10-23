from decimal import Decimal
from pathlib import Path

import pytest

from imports.adapters.csv import parse_csv

FIXTURE = Path(__file__).parent / "fixtures" / "statement.csv"


def test_csv_adapter_normalizes_anonimized_fixture():
    entries = parse_csv(FIXTURE.read_bytes())

    assert len(entries) == 2
    assert entries[0].external_id == "txn-001"
    assert entries[0].amount == Decimal("-42.50")
    assert entries[0].transaction_date.isoformat() == "2026-01-05"
    assert entries[1].description == "Receita anonima"


def test_csv_adapter_rejects_missing_required_column():
    with pytest.raises(ValueError, match="external_id"):
        parse_csv(b"date,amount,description\n2026-01-01,10,Teste\n")
