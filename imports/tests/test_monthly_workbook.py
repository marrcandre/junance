from datetime import date
from decimal import Decimal
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from imports.adapters.xlsx import parse_xlsx


def _monthly_workbook():
    workbook = """<?xml version="1.0" encoding="UTF-8"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <sheets><sheet name="0126" sheetId="1" r:id="rId1"/></sheets>
    </workbook>"""
    relationships = """<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
      <Relationship Id="rId1" Target="worksheets/sheet1.xml"
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>
    </Relationships>"""
    sheet = """<?xml version="1.0" encoding="UTF-8"?>
    <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
      <sheetData>
        <row r="1"><c r="A1" t="inlineStr"><is><t>Sobra</t></is></c><c r="B1"><v>50</v></c>
          <c r="D1" t="inlineStr"><is><t>Despesas fixas</t></is></c></row>
        <row r="2"><c r="A2" t="inlineStr"><is><t>Entradas Totais</t></is></c>
          <c r="B2"><v>100</v></c>
          <c r="D2" t="inlineStr"><is><t>Água</t></is></c><c r="E2"><v>20</v></c></row>
        <row r="3"><c r="A3" t="inlineStr"><is><t>Salário</t></is></c><c r="B3"><v>100</v></c></row>
        <row r="4"><c r="A4" t="inlineStr"><is><t>Pagamentos</t></is></c>
          <c r="B4"><v>50</v></c></row>
        <row r="5"><c r="A5" t="inlineStr"><is><t>Mercado</t></is></c><c r="B5"><v>50</v></c></row>
      </sheetData>
    </worksheet>"""
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", relationships)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
    return output.getvalue()


def test_monthly_workbook_adapter_imports_detail_and_skips_totals():
    entries = parse_xlsx(_monthly_workbook())

    assert {(entry.description, entry.amount) for entry in entries} == {
        ("Salário", Decimal("100")),
        ("Mercado", Decimal("-50")),
        ("Água", Decimal("-20")),
    }
    salary = next(entry for entry in entries if entry.description == "Salário")
    assert salary.transaction_date == date(2026, 1, 1)
    assert salary.raw_data["source_sheet"] == "0126"
