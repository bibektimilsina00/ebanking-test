import csv
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.conf import settings
import os
from datetime import datetime
from accounts.models import CustomUser


def export_to_csv(transactions):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "BS Date",
            "Transaction Date",
            "Particulars",
            "Cheque Number",
            "Debit",
            "Credit",
            "Balance",
        ]
    )
    for txn in transactions:
        writer.writerow(
            [
                txn.get("BSDate"),
                txn.get("TransactionDate"),
                txn.get("Particulars"),
                txn.get("ChequeNumber"),
                txn.get("Debit"),
                txn.get("Credit"),
                txn.get("Balance"),
            ]
        )

    return response


def export_to_excel(transactions):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="transactions.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"

    ws.append(
        [
            "BS Date",
            "Transaction Date",
            "Particulars",
            "Cheque Number",
            "Debit",
            "Credit",
            "Balance",
        ]
    )
    for txn in transactions:
        ws.append(
            [
                txn.get("BSDate"),
                txn.get("TransactionDate"),
                txn.get("Particulars"),
                txn.get("ChequeNumber"),
                txn.get("Debit"),
                txn.get("Credit"),
                txn.get("Balance"),
            ]
        )

    wb.save(response)
    return response


from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Image,
    Paragraph,
    Spacer,
)
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse
import os
from django.conf import settings
from datetime import datetime


def export_to_pdf(
    user, transactions, account_number, start_date, end_date, group_name, interest_rate
):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="transactions.pdf"'

    # Create a PDF document with specific margins
    left_margin = 50
    doc = SimpleDocTemplate(
        response, pagesize=letter, leftMargin=left_margin, topMargin=10
    )

    elements = []
    styles = getSampleStyleSheet()

    logo_path = os.path.join(settings.MEDIA_ROOT, user.avtar.name)
    # Draw the logo on the left side
    logo = Image(logo_path, 1 * inch, 1 * inch)  # Width and height of the logo
    logo.hAlign = "LEFT"

    # Main Title with additional text
    title_text = (
        f" <font size='16' color='#0f3f88'>{user.first_name} {user.last_name}</font>"
    )
    additional_text = f"<font size='12' color='#0f3f88'>{user.address}</font>"
    title_with_additional = Paragraph(
        f"{title_text}<br/>{additional_text}", styles["Title"]
    )

    space = ""
    # Create a table for the logo and title_with_additional as two columns
    logo_and_title = Table(
        [[logo, title_with_additional, space]], colWidths=[4 * cm, 16 * cm, 0 * cm]
    )
    logo_and_title.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    # Add the logo and title table to the elements list
    elements.append(logo_and_title)

    custom_style_subtitle = ParagraphStyle(
        "CustomStyleSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=12,  # Decrease line spacing (default is typically 1.2 times the font size)
    )

    # Subtitle
    subtitle_text = f"""
    <div align="left">
    <font size='10'>
    <b>Account Number:</b> {account_number}<br/>
    <b>Account Group:</b> {group_name} <br/>
    <b>Interest Rate:</b> {interest_rate}<br/>
    </font>
    </div>
    """
    subtitle = Paragraph(subtitle_text, custom_style_subtitle)

    today = datetime.today()
    formatted_date = today.strftime("%Y-%m-%d")

    date_string = f""" 
    <div align="right">
    <font size='10'>
    <b>Issue Date:</b> {formatted_date}<br/>
    <b>From :</b> {start_date} To {end_date}<br/>
    </font>
    </div>
    """

    issue_date = Paragraph(date_string, custom_style_subtitle)

    issue_date_and_subtitle = Table(
        [[subtitle, issue_date]], colWidths=[10 * cm, 7 * cm]
    )

    elements.append(issue_date_and_subtitle)
    elements.append(Spacer(1, 12))

    # Table header
    table_header = [
        "BS Date",
        "Transaction Date",
        "Particulars",
        "Debit",
        "Credit",
        "Balance ",
    ]

    # Table data
    data = [table_header]

    # Fill the data list with transactions
    for txn in transactions:
        row = [
            txn.get("BSDate", "N/A"),
            txn.get("TransactionDate", "N/A"),
            txn.get("Particulars", "N/A"),
            str(txn.get("Debit", "0")),
            str(txn.get("Credit", "0")),
            str(txn.get("Balance", "0")),
        ]
        data.append(row)

    # Table style with header color
    table_style = TableStyle(
        [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.darkblue,
            ),  # Header row background color
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # Header row text color
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("GRID", (0, 1), (-1, -1), 1, colors.black),
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.lightblue,
            ),  # Background color for data rows
        ]
    )

    # Apply alternating background colors for rows
    for index in range(1, len(data)):
        bg_color = colors.lightblue if index % 2 == 0 else colors.white
        table_style.add("BACKGROUND", (0, index), (-1, index), bg_color)

    col_widths = [1 * inch, 1 * inch, 2 * inch, 1 * inch, 1 * inch, 1 * inch]

    # Create the table
    table = Table(data, style=table_style, colWidths=col_widths, repeatRows=1)
    table.hAlign = "LEFT"
    elements.append(table)

    # Add the "Transaction Summary" heading
    elements.append(Spacer(1, 12))  # Add some space before the summary
    summary_heading = Paragraph("<b>Transaction Summary</b>", styles["Title"])
    elements.append(summary_heading)

    # Add the summary table
    summary_data = [
        ["Opening Balance", "Debit Entry", "Credit Entry", "Closing Balance"],
        ["", "", "", ""],  # Placeholder row for values
    ]

    summary_table_style = TableStyle(
        [
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            (
                "LINEBELOW",
                (0, 0),
                (-1, 0),
                1,
                colors.black,
            ),  # Line below the "Transaction Summary" heading
            (
                "LINEBELOW",
                (0, 1),
                (-1, 1),
                0,
                colors.white,
            ),  # No lines between the columns
            (
                "LINEBELOW",
                (0, 2),
                (-1, 2),
                0,
                colors.white,
            ),  # No lines between the columns
        ]
    )

    summary_col_widths = [2 * inch, 2 * inch, 2 * inch, 2 * inch]

    summary_table = Table(
        summary_data, style=summary_table_style, colWidths=summary_col_widths
    )
    elements.append(summary_table)

    # Build the PDF
    doc.build(elements)

    return response
