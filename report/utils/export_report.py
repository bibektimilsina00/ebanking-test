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

def export_to_pdf(transactions):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50  # Start position for the Y-axis
    
    p.drawString(30, y, 'BS Date | Transaction Date | Particulars  | Debit | Credit | Balance')
    y -= 20
    
    for txn in transactions:
        if y < 40:  # Min Y boundary before adding a new page
            p.showPage()
            y = height - 50
        p.drawString(30, y, f"{txn.get('BSDate')} | {txn.get('TransactionDate')} | {txn.get('Particulars')} | {txn.get('Debit')} | {txn.get('Credit')} | {txn.get('Balance')}")
        y -= 20
    
    p.showPage()
    p.save()
    return response


