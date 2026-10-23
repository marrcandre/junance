from datetime import date
from decimal import Decimal
from xml.etree import ElementTree

from imports.adapters.base import NormalizedEntry


def parse_ofx(content):
    root = ElementTree.fromstring(content)
    entries = []
    for transaction in root.iter():
        if transaction.tag.upper().endswith("STMTTRN"):
            values = {
                child.tag.split("}")[-1].upper(): (child.text or "").strip()
                for child in transaction
            }
            posted = values["DTPOSTED"][:8]
            entries.append(
                NormalizedEntry(
                    external_id=values.get("FITID", posted),
                    transaction_date=date.fromisoformat(
                        f"{posted[:4]}-{posted[4:6]}-{posted[6:8]}"
                    ),
                    amount=Decimal(values["TRNAMT"]),
                    description=values.get("NAME") or values.get("MEMO", ""),
                    raw_data=values,
                )
            )
    return entries
