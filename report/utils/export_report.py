import csv
from django.http import HttpResponse

def export_to_csv(transactions):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['BS Date', 'Transaction Date', 'Particulars', 'Cheque Number', 'Debit', 'Credit', 'Balance'])
    for txn in transactions:
        writer.writerow([
            txn.get('BSDate'), 
            txn.get('TransactionDate'), 
            txn.get('Particulars'), 
            txn.get('ChequeNumber'), 
            txn.get('Debit'), 
            txn.get('Credit'), 
            txn.get('Balance')
        ])
    
    return response

from openpyxl import Workbook
from django.http import HttpResponse

def export_to_excel(transactions):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"
    
    ws.append(['BS Date', 'Transaction Date', 'Particulars', 'Cheque Number', 'Debit', 'Credit', 'Balance'])
    for txn in transactions:
        ws.append([
            txn.get('BSDate'), 
            txn.get('TransactionDate'), 
            txn.get('Particulars'), 
            txn.get('ChequeNumber'), 
            txn.get('Debit'), 
            txn.get('Credit'), 
            txn.get('Balance')
        ])
    
    wb.save(response)
    return response



from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime

def export_to_pdf(transactions, account_number, start_date, end_date):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'

    # Create a PDF document with specific margins
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=90, leftMargin=90, topMargin=30, bottomMargin=18)
    elements = []
    
    
    
    styles = getSampleStyleSheet()
    
    headerStyle = ParagraphStyle(
    'headerStyle',
    parent=styles['Heading1'],  # Start with pre-defined heading style
    fontName='Helvetica-Bold',  # Choose a bold font to make the header stand out
    fontSize=18,  # Increase the font size for better visibility
    leading=22,  # Space between lines in the paragraph
    spaceAfter=20,  # Space after the paragraph
    alignment=1,  # Center-align the text
    textColor=colors.red,  # Navy color for the text
    backColor=colors.lightgrey,  # Light grey background for the header
    borderPadding=(10, 0, 10, 0),  # Padding around the text (top, left, bottom, right)
    borderRadius=5  # Rounded corners for the background
    
)
    
    header_text = "Account Statement Overview"
    header = Paragraph(header_text, headerStyle)
    elements.append(header)
    
    # Add account details
    account_details = [
        ['Account Number:', account_number],
        ['Start Date:', start_date],
        ['End Date:', end_date]
    ]
    for detail in account_details:
        elements.append(Paragraph(f"<b>{detail[0]}</b> {detail[1]}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Add dow

    # Table header
    table_header = [
        "BS Date", "Transaction Date", "Particulars", "Debit", "Credit", "Balance"
    ]

    # Table data
    data = [table_header]



    # Fill the data list with transactions
    for index, txn in enumerate(transactions):
        # Ensure all keys exist
        row = [
            txn.get('BSDate', 'N/A'),
            txn.get('TransactionDate', 'N/A'),
            txn.get('Particulars', 'N/A'),
            str(txn.get('Debit', '0')),
            str(txn.get('Credit', '0')),
            str(txn.get('Balance', '0'))
        ]
        data.append(row)

 

    # Table style with header color
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white)  # Background color for data rows
    ])

    # Apply alternating background colors for rows
    for index in range(1, len(data)):
        bg_color = colors.lightblue if index % 2 == 0 else colors.white
        table_style.add('BACKGROUND', (0, index), (-1, index), bg_color)

    # Create the table
    table = Table(data, style=table_style)
    elements.append(table)

    # Build the PDF
    doc.build(elements)
    return response


