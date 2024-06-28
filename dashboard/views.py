from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import requests
import json
from organizations.models import Organization
from branches.models import Branch
from report.models import ReportViewModel
from staff.models import Staff
from accounts.models import CustomUser






class OrganizationDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/organization_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        
        # all users whose role is not superadmin or organization
        all_users = CustomUser.objects.exclude(role__in=['superadmin', 'organization'])
        
        context['all_users'] = all_users
        # all users whose rose is not superadmin or organization and active
        all_active_users = CustomUser.objects.exclude(role__in=['superadmin', 'organization']).filter(is_active=True)
        context['all_active_users'] = all_active_users
        
        # all branch whose creator is the current user
        all_branches = Branch.objects.filter(created_by=self.request.user)
        context['all_branches'] = all_branches
        
        # all staff whose branch is created by the current user
        all_staff = Staff.objects.filter(branch__created_by=self.request.user)
        context['all_staff'] = all_staff
    
        
        # all active branches whose creator is the current user
        branches = Branch.objects.filter(created_by=self.request.user)
        created_account_users = CustomUser.objects.filter(branches__in=branches, is_active=True).distinct()
        context['all_active_branches'] = created_account_users
        # all inactive branches whose creator is the current user
        created_account_users = CustomUser.objects.filter(branches__in=branches, is_active=False).distinct()
        context['all_inactive_branches'] = created_account_users
        
        # all active staff whose branch is created by the current user
        branches = Branch.objects.filter(created_by=self.request.user)
        created_account_users = CustomUser.objects.filter(staff_profile__branch__in=branches, is_active=True).distinct()
        context['all_active_staff'] = created_account_users
        # all inactive staff whose branch is created by the current user
        created_account_users = CustomUser.objects.filter(staff_profile__branch__in=branches, is_active=False).distinct()
        context['all_inactive_staff'] = created_account_users
        
        all_inactive_users_count = len(all_users) - len(all_active_users)
        
        context['all_inactive_users_count'] = all_inactive_users_count
        
        
        organization = Organization.objects.get(owner=self.request.user)
        if organization:
            total_report_count = ReportViewModel.objects.filter(organization=organization).count()
            today = timezone.now().date()
            today_report_count = ReportViewModel.objects.filter(organization=organization, viewed_at__date=today).count()
        else:
            total_report_count = 0
            today_report_count = 0
            
        context['total_report_count'] = total_report_count
        context['today_report_count'] = today_report_count

        return context

class BranchDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/branch_dashboard.html'

    def get_context_data(self, **kwargs):
        total_balance = 0
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
        total_balance = sum(account['PBal'] for account in context['accounts'] if 'PBal' in account)
        
        # all user created by the current user and whole role is staff
        all_staff = Staff.objects.filter(branch__owner=self.request.user)
        context['all_staff'] = all_staff
        context['total_balance'] = total_balance
        
        
        
        
        
        
        
        
        
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
        total_balance=0
        context = super().get_context_data(**kwargs)
        
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
        total_balance = sum(account['PBal'] for account in filtered_accounts if 'PBal' in account)
        context['total_balance'] = total_balance
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
