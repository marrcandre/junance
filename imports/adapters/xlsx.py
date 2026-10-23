from datetime import date
from decimal import Decimal
from io import BytesIO
from xml.etree import ElementTree
from zipfile import ZipFile

from imports.adapters.base import NormalizedEntry


def parse_xlsx(content):
    with ZipFile(BytesIO(content)) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.itertext()) for node in root]
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.iter():
            if row.tag.endswith("row"):
                values = []
                for cell in row:
                    if not cell.tag.endswith("c"):
                        continue
                    value = next((node.text for node in cell if node.tag.endswith("v")), "")
                    if cell.attrib.get("t") == "s":
                        value = shared[int(value)]
                    values.append(value)
                rows.append(values)
    headers = rows[0]
    records = [dict(zip(headers, row, strict=False)) for row in rows[1:]]
    return [
        NormalizedEntry(
            external_id=row["external_id"],
            transaction_date=date.fromisoformat(row["date"]),
            amount=Decimal(row["amount"]),
            description=row["description"],
            raw_data=row,
        )
        for row in records
    ]
