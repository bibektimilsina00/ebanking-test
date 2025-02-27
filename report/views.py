# report/views.py
import csv
from nepali_datetime import date as NepaliDate
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
from django.contrib.auth.decorators import login_required

from .utils.export_report import export_to_csv, export_to_excel, export_to_pdf


class ReportView(View):
    template_name = "report/report.html"

    def get_context_data(self, **kwargs):
        context = {}
        total_balance = 0
        account_number = self.request.GET.get("account", None)

        context["selected_account_number"] = account_number
        accounts = []
        if self.request.user.role == "staff":
            branch = Branch.objects.get(staff_members__user=self.request.user)
            organization = branch.organization
            staff = Staff.objects.get(user=self.request.user)
            access_accounts = set(staff.access_accounts.split(","))

            all_accounts = self.fetch_member_ledger(organization, branch.member_number)
            filtered_accounts = [
                acc for acc in all_accounts if acc["AccNum"] in access_accounts
            ]
            accounts = filtered_accounts
        if self.request.user.role == "branch":
            try:
                branch = Branch.objects.get(owner=self.request.user)
                organization = branch.organization
            except Branch.DoesNotExist:
                context["error"] = "Branch not found"
                return context
            except Organization.DoesNotExist:
                context["error"] = "Organization not found"
                return context
            access_accounts = set(branch.available_accounts.split(","))
            all_accounts = self.fetch_member_ledger(organization, branch.member_number)
            filtered_accounts = [
                acc for acc in all_accounts if acc["AccNum"] in access_accounts
            ]
            accounts = filtered_accounts

        # all user created by the current user and whole role is staff
        all_staff = Staff.objects.filter(branch__owner=self.request.user)
        context["all_staff"] = all_staff
        context["total_balance"] = total_balance
        context["accounts"] = accounts

        return context

    def fetch_member_ledger(self, organization, member_number):
        api_url = f"{organization.base_url}MemberLedgerEbank"
        payload = {
            "clientId": organization.clint_id,
            "Flag": "ALL",
            "MembNum": member_number,
            "username": organization.username,
        }

        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()
            if response.status_code == 200 and response_data.get("isSuccess"):
                return json.loads(response_data.get("result"))
        except requests.RequestException as e:
            return []
        return []

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        transactions = []
        form = ReportForm()
        context.update({"form": form, "transactions": transactions})
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

        ReportViewModel.objects.create(
            user=self.request.user, organization=organization
        )

        account_number = request.POST.get("account")
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")
        date_type = request.POST.get("date_type")
        client_id = organization.clint_id
        username = organization.username
        if date_type == "BS":
            start_date_str = self.convert_bs_to_ad(start_date_str)
            end_date_str = self.convert_bs_to_ad(end_date_str)
        payload = {
            "AccNum": account_number,
            "EndDate": end_date_str,
            "StartDate": start_date_str,
            "clientId": client_id,
            "username": username,
        }
        print(request.POST)
        api_url = f"{organization.base_url}SavingLedgerEbank"
        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()
            if response_data.get("isSuccess"):
                transactions = json.loads(response_data["result"])
        except requests.RequestException as e:
            context.update({"transactions": transactions, "error": str(e)})
            return render(request, self.template_name, context)

        context.update({"transactions": transactions})
        return JsonResponse({"transactions": list(transactions)})

    def convert_bs_to_ad(self, bs_date_str):
        # Assuming the bs_date_str format is 'YYYY-MM-DD' in Nepali date.
        year, month, day = map(int, bs_date_str.split("-"))
        nepali_date = NepaliDate(year, month, day)
        ad_date = nepali_date.to_datetime_date()
        return ad_date.strftime("%Y-%m-%d")


@login_required
@require_http_methods(["POST"])
def export_report(request):
    try:

        # required data
        # transactions, account_number, start_date, end_date Orgnization Address, Orginization icon

        organization = None
        if request.user.role == "branch":
            branch = Branch.objects.get(owner=request.user)
            organization = branch.organization
        else:
            branch = Branch.objects.get(staff_members__user=request.user)
            organization = branch.organization
        org_owner = organization.owner

        data = json.loads(request.body)  # Load JSON data from request body
        transactions = data.get("transactions", [])
        account_number = data.get("account_number", "")
        start_date = data.get("start_date", "")
        end_date = data.get("end_date", "")
        intrest_rate = data.get("intrest_rate", "")
        group_name = data.get("account_group", "")

        report_type = data.get("type", "")
        if report_type == "csv":
            return export_to_csv(transactions)
        elif report_type == "excel":
            return export_to_excel(transactions)
        elif report_type == "pdf":
            return export_to_pdf(
                user=org_owner,
                transactions=transactions,
                account_number=account_number,
                start_date=start_date,
                end_date=end_date,
                group_name=group_name,
                interest_rate=intrest_rate,
            )

        return HttpResponse("Invalid report type", status=400)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON", status=400)
