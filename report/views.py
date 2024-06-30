# report/views.py
import csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from organizations.models import Organization
from .forms import ReportForm
import requests
import json
from datetime import datetime
from branches.models import Branch
from staff.models import Staff
from .models import ReportViewModel
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .utils.export_report import export_to_csv,export_to_excel,export_to_pdf

class ReportView(View):
    template_name = 'report/report.html'
    
    def get_context_data(self, **kwargs):
        context = {}
        
        if  self.request.user.role == "branch":
            try:
                branch = Branch.objects.get(owner=self.request.user)
                organization = branch.organization
            except Branch.DoesNotExist:
                context['error'] = 'Branch not found'
                return context
            except Organization.DoesNotExist:
                context['error'] = 'Organization not found'
                return context

            context['accounts'] = self.fetch_member_ledger(organization, branch.member_number)
            
            
            
            return context
            
        if self.request.user.role == "staff":
            try:
                branch = Branch.objects.get(staff_members__user=self.request.user)
                organization = branch.organization
                staff = Staff.objects.get(user=self.request.user)
                access_accounts = set(staff.access_accounts.split(','))  # Ensure unique accounts
            except Branch.DoesNotExist:
                context['accounts'] = []
                return context

            all_accounts = self.fetch_member_ledger(organization, branch.member_number)
            filtered_accounts = [acc for acc in all_accounts if acc['AccNum'] in access_accounts]
            context['accounts'] = filtered_accounts
            return context

    def fetch_member_ledger(self, organization, member_number):
        api_url = f"{organization.base_url}MemberLedgerEbank"
        payload = {
            "clientId": organization.clint_id,
            "Flag": "ALL",
            "MembNum": member_number,
            "username": organization.username
        }

        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()
            if response.status_code == 200 and response_data.get('isSuccess'):
                return json.loads(response_data.get('result'))
        except requests.RequestException as e:
            return []
        return []

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        transactions = []
        form = ReportForm()
        context.update({'form': form, 'transactions': transactions})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        transactions = []

        if self.request.user.role == "branch":
            branch = Branch.objects.get(owner=self.request.user)
            organization = branch.organization
        else:
            branch = Branch.objects.get(staff_members__user=self.request.user)
            organization = branch.organization

        ReportViewModel.objects.create(user=self.request.user, organization=organization)

        account_number = request.POST.get('AccountNo')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
 
        # Convert start_date and end_date from strings to datetime objects
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError as e:
            context.update({'transactions': transactions, 'error': 'Invalid date format'})
            return render(request, self.template_name, context)

        client_id = organization.clint_id
        username = organization.username
        payload = {
             "AccNum": "KBS0000124",
    "EndDate": "2023-05-22",
    "StartDate": "2013-05-22",
    "clientId": "66",
  "username":"shrawan" 
        }

        api_url = f"{organization.base_url}SavingLedgerEbank"
        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()
            if response_data.get('isSuccess'):
                transactions = json.loads(response_data['result'])
        except requests.RequestException as e:
            context.update({'transactions': transactions, 'error': str(e)})
            return render(request, self.template_name, context)


        context.update({'transactions': transactions})
        return JsonResponse({'transactions': list(transactions)})
    
    


@require_http_methods(["POST"])  
def export_report(request):
    try:
        
    
        data = json.loads(request.body)  # Load JSON data from request body
        transactions = data.get('transactions', [])
        account_number = data.get('account_number', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        
        report_type = data.get('type', '')
        if report_type == 'csv':
            return export_to_csv(transactions)
        elif report_type == 'excel':
            return export_to_excel(transactions)
        elif report_type == 'pdf':
            return export_to_pdf(transactions, account_number, start_date, end_date)

        return HttpResponse("Invalid report type", status=400)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON", status=400)
    
    
    


