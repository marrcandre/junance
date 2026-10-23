import csv
from datetime import date
from decimal import Decimal
from io import StringIO

from imports.adapters.base import NormalizedEntry

REQUIRED_COLUMNS = {"external_id", "date", "amount", "description"}


def parse_csv(content):
    reader = csv.DictReader(StringIO(content.decode("utf-8-sig")))
    columns = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(missing))}")
    return [
        NormalizedEntry(
            external_id=row["external_id"].strip(),
            transaction_date=date.fromisoformat(row["date"].strip()),
            amount=Decimal(row["amount"].strip()),
            description=row["description"].strip(),
            raw_data=dict(row),
        )
        for row in reader
    ]
