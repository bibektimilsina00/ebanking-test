from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import requests
import json
from organizations.models import Organization
from branches.models import Branch
from staff.models import Staff

class OrganizationDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/organization_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class BranchDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/branch_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

class StaffDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/staff_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            branch = Branch.objects.get(staff_members__user=self.request.user)
            organization = branch.organization
            staff = Staff.objects.get(user=self.request.user)
            access_accounts = staff.access_accounts.split(',')
        except Branch.DoesNotExist:
            context['accounts'] = []
            return context

        all_accounts = self.fetch_member_ledger(organization, branch.member_number)
        context['accounts'] = [acc for acc in all_accounts if acc['AccNum'] in access_accounts]
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








from django.shortcuts import redirect

from django.views import View


class RedirectDashboardView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        role_dashboard_map = {
            'superadmin': 'admin:index',
            'organization': 'organization_dashboard',
            'branch': 'branch_dashboard',
            'staff': 'staff_dashboard'
        }
        return redirect(role_dashboard_map.get(user.role, 'login'))
