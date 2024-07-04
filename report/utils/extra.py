from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse
import os
from django.conf import settings
from datetime import datetime

def export_to_pdf(user, transactions, account_number, start_date, end_date, group_name, interest_rate):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'
    
    # Create a PDF document with specific margins
    left_margin = 50
    doc = SimpleDocTemplate(response, pagesize=letter, leftMargin=left_margin, topMargin=10)

    elements = []
    styles = getSampleStyleSheet()
    
    logo_path = os.path.join(settings.MEDIA_ROOT, user.avtar.name)
    # Draw the logo on the left side
    logo = Image(logo_path, 1 * inch, 1 * inch)  # Width and height of the logo
    logo.hAlign = 'LEFT'
    
    # Main Title with additional text
    title_text = f" <font size='16' color='#0f3f88'>{user.first_name} {user.last_name}</font>"
    additional_text = f"<font size='12' color='#0f3f88'>{user.address}</font>"
    title_with_additional = Paragraph(f"{title_text}<br/>{additional_text}", styles['Title'])
    
    space = ''
    # Create a table for the logo and title_with_additional as two columns
    logo_and_title = Table([[logo, title_with_additional, space]], colWidths=[4 * cm, 16 * cm, 0 * cm])
    logo_and_title.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    # Add the logo and title table to the elements list
    elements.append(logo_and_title)
    
    custom_style_subtitle = ParagraphStyle(
        'CustomStyleSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12  # Decrease line spacing (default is typically 1.2 times the font size)
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
    formatted_date = today.strftime('%Y-%m-%d')
    
    date_string = f""" 
    <div align="right">
    <font size='10'>
    <b>Issue Date:</b> {formatted_date}<br/>
    <b>From :</b> {start_date} To {end_date}<br/>
    </font>
    </div>
    """
    
    issue_date = Paragraph(date_string, custom_style_subtitle)
    
    issue_date_and_subtitle = Table([[subtitle, issue_date]], colWidths=[10 * cm, 7 * cm])
    
    elements.append(issue_date_and_subtitle)
    elements.append(Spacer(1, 12))

    # Table header
    table_header = [
        "BS Date", "Transaction Date", "Particulars", "Debit", "Credit", "Balance "
    ]

    # Table data
    data = [table_header]

    # Fill the data list with transactions
    for txn in transactions:
        row = [
            txn.get('BSDate', 'N/A'),
            txn.get('TransactionDate', 'N/A'),
            txn.get('Particulars', 'N/A'),
            str(txn.get('Debit', '0')),
            str(txn.get('Credit', '0')),
            str(txn.get('Balance', '0'))
        ]
        data.append(row)

    # Add the "Transaction History" heading as a row
    transaction_history_heading = [Paragraph("<font size='16' color='#0f3f88'><b>Transaction History</b></font>", styles['Title'])]

    # Add the summary row
    summary_row_heading = ["Opening Balance", "Debit Entry", "Credit Entry", "Closing Balance"]
    summary_row_values = ["", "", "", ""]  # Placeholder row for values

    # Add the rows to the data
    data.append(transaction_history_heading)
    data.append(summary_row_heading)
    data.append(summary_row_values)

    # Table style with header color
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (1, -3), (-1, -3), colors.darkblue),  # Background color for "Transaction History" heading
        ('TEXTCOLOR', (1, -3), (-1, -3), colors.whitesmoke),  # Text color for "Transaction History" heading
        ('FONTNAME', (1, -3), (-1, -3), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -2), (-1, -2), colors.lightblue),  # Background color for summary header
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),  # Background color for summary values
        ('LINEBELOW', (0, -2), (-1, -2), 0, colors.white),  # No lines between the summary columns
        ('LINEBELOW', (0, -1), (-1, -1), 0, colors.white)   # No lines between the summary columns
    ])

    # Apply alternating background colors for rows
    for index in range(1, len(data) - 3):  # Exclude the last 3 rows (Transaction History and summary rows)
        bg_color = colors.lightblue if index % 2 == 0 else colors.white
        table_style.add('BACKGROUND', (0, index), (-1, index), bg_color)
        
    col_widths = [1 * inch, 1 * inch, 2 * inch, 1 * inch, 1 * inch, 1 * inch]

    # Create the table
    table = Table(data, style=table_style, colWidths=col_widths, repeatRows=1)
    table.hAlign = 'LEFT'
    elements.append(table)

    # Build the PDF
    doc.build(elements)
    
    return response