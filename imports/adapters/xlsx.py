import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from io import BytesIO
from xml.etree import ElementTree
from zipfile import ZipFile

from imports.adapters.base import NormalizedEntry

SUMMARY_LABELS = {
    "cartões",
    "despesas fixas",
    "entradas totais",
    "investimentos",
    "pagamentos",
    "rendimento",
    "rendimento real",
    "reserva do mês",
    "retirada mês anterior",
    "saldo anterior",
    "saldo da conta",
    "saldo restante",
    "sobra",
    "total em contas",
}


def _shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(node.itertext()) for node in root]


def _column(ref):
    letters = re.match(r"[A-Z]+", ref.upper())
    value = 0
    for letter in letters.group(0):
        value = value * 26 + ord(letter) - ord("A") + 1
    return value - 1


def _rows(sheet, shared):
    rows = []
    for row in sheet.iter():
        if not row.tag.endswith("row"):
            continue
        values = {}
        for cell in row:
            if not cell.tag.endswith("c"):
                continue
            value_node = next((node for node in cell if node.tag.endswith("v")), None)
            value = value_node.text if value_node is not None else None
            if cell.attrib.get("t") == "s" and value is not None:
                value = shared[int(value)]
            elif cell.attrib.get("t") == "inlineStr":
                value = "".join(cell.itertext()).replace(value or "", "", 1) or value
            values[_column(cell.attrib["r"])] = value
        rows.append(values)
    return rows


def _money(value):
    if value in (None, ""):
        return None
    if isinstance(value, Decimal):
        return value
    text = str(value).strip().replace("R$", "").replace(" ", "")
    if not text:
        return None
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _date_value(value, fallback):
    if value in (None, ""):
        return fallback
    text = str(value).strip()
    try:
        return date.fromisoformat(text)
    except ValueError:
        pass
    try:
        return datetime.strptime(text, "%d/%m/%Y").date()
    except ValueError:
        serial = Decimal(text)
        return (datetime(1899, 12, 30) + timedelta(days=float(serial))).date()


def _is_summary(label):
    normalized = " ".join(label.lower().split())
    return (
        normalized in SUMMARY_LABELS
        or normalized.startswith("total")
        or normalized.startswith("saldo")
    )


def _monthly_sheets(archive):
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        relation.attrib["Id"]: relation.attrib["Target"]
        for relation in relationships
        if relation.tag.endswith("Relationship")
    }
    result = []
    for sheet in workbook.iter():
        if not sheet.tag.endswith("sheet"):
            continue
        name = sheet.attrib["name"]
        if not re.fullmatch(r"\d{4}", name):
            return []
        target = targets[
            sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        ]
        result.append((name, target.removeprefix("/")))
    return result


def _parse_monthly(archive, shared, sheets):
    entries = []
    for sheet_name, target in sheets:
        month = datetime.strptime(sheet_name, "%m%y").date().replace(day=1)
        target = target.lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        sheet = ElementTree.fromstring(archive.read(target))
        mode = "income"
        for row_number, row in enumerate(_rows(sheet, shared), 1):
            label_a = str(row.get(0) or "").strip()
            label_d = str(row.get(3) or "").strip()
            if label_a.lower() == "pagamentos":
                mode = "expense"
                continue
            if label_a and not _is_summary(label_a):
                amount = _money(row.get(1))
                if amount not in (None, Decimal("0")):
                    entries.append(
                        NormalizedEntry(
                            f"{sheet_name}:a:{row_number}",
                            month,
                            amount if mode == "income" else -abs(amount),
                            label_a,
                            {
                                "source_sheet": sheet_name,
                                "source_section": mode,
                                "competence_date": month.isoformat(),
                            },
                        )
                    )
            if label_d and not _is_summary(label_d):
                amount = _money(row.get(4))
                if amount not in (None, Decimal("0")):
                    entries.append(
                        NormalizedEntry(
                            f"{sheet_name}:d:{row_number}",
                            _date_value(row.get(5), month),
                            -abs(amount),
                            label_d,
                            {
                                "source_sheet": sheet_name,
                                "source_section": "fixed_expense",
                                "competence_date": month.isoformat(),
                            },
                        )
                    )
    return entries


def parse_xlsx(content):
    with ZipFile(BytesIO(content)) as archive:
        shared = _shared_strings(archive)
        sheets = _monthly_sheets(archive) if "xl/workbook.xml" in archive.namelist() else []
        if sheets:
            return _parse_monthly(archive, shared, sheets)
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        parsed_rows = _rows(sheet, shared)
        rows = [
            [row.get(index, "") for index in range(max(row, default=-1) + 1)] for row in parsed_rows
        ]
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
