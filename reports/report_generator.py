"""
reports/report_generator.py
----------------------------
Generates exportable reports (Prototype 6): assessment summary,
training results, and vulnerability report, in PDF, Excel, and CSV.
"""

import csv
import io
from datetime import datetime

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def _pdf_table(title, headers, rows):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Cybersecurity Assessment and Awareness System (CAAS)", styles["Title"]),
        Paragraph(title, styles["Heading2"]),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 16),
    ]

    data = [headers] + [[str(cell) for cell in row] for row in rows]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def _excel_table(title, headers, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]
    ws.append(headers)
    for row in rows:
        ws.append(list(row))
    for col_cells in ws.columns:
        max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = max_len + 2
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def _csv_table(headers, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    mem = io.BytesIO(buffer.getvalue().encode("utf-8"))
    mem.seek(0)
    return mem


def build_report(report_type: str, fmt: str, headers, rows):
    """report_type: 'assessment' | 'training' | 'vulnerability'
    fmt: 'pdf' | 'excel' | 'csv'
    """
    titles = {
        "assessment": "SME Assessment Summary Report",
        "training": "Employee Training Results Report",
        "vulnerability": "Network Vulnerability Report",
    }
    title = titles.get(report_type, "CAAS Report")

    if fmt == "pdf":
        return _pdf_table(title, headers, rows), "application/pdf", "pdf"
    elif fmt == "excel":
        return _excel_table(title, headers, rows), (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ), "xlsx"
    elif fmt == "csv":
        return _csv_table(headers, rows), "text/csv", "csv"
    else:
        raise ValueError("Unsupported format: " + fmt)
