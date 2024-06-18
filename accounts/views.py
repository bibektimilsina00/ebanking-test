from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
import requests
import json

from accounts.models import CustomUser, Account, Branch, Organization, Staff

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        role_dashboard_map = {
            'organization': 'organization_dashboard',
            'branch': 'branch_dashboard',
            'staff': 'staff_dashboard'
        }
        return reverse_lazy(role_dashboard_map.get(user.role, 'admin:index'))

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return self.render_to_response(self.get_context_data(form=form))

class OrganizationDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'organization_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class BranchDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'branch_dashboard.html'

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
    template_name = 'staff_dashboard.html'

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

class UserListView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/user_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        if current_user.role == 'organization':
            branches = Branch.objects.filter(created_by=current_user)
            created_account_users = CustomUser.objects.filter(branches__in=branches).distinct()
        elif current_user.role == 'branch':
            branches = Branch.objects.filter(owner=current_user)
            created_account_users = CustomUser.objects.filter(staff_profile__branch__in=branches).distinct()
        else:
            created_account_users = CustomUser.objects.none()

        context['users'] = created_account_users
        return context

class ResetPasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        try:
            user = CustomUser.objects.get(id=user_id)
            new_password = get_random_string(length=8)
            user.set_password(new_password)
            user.save()
            send_mail(
                'Your password has been reset',
                f'Your new password is: {new_password}',
                'admin@yourdomain.com',
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'Password reset and email sent.'})
        except CustomUser.DoesNotExist:
            return HttpResponseBadRequest('User does not exist')

class SuspendUserView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return JsonResponse({'status': 'success', 'message': 'User suspended successfully.'})
        except CustomUser.DoesNotExist:
            return HttpResponseBadRequest('User does not exist')

class ActivateUserView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return JsonResponse({'status': 'success', 'message': 'User activated successfully.'})
        except CustomUser.DoesNotExist:
            return HttpResponseBadRequest('User does not exist')

class CreateUserView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        available_accounts = request.POST.getlist('accounts')

        if request.user.role == 'organization':
            role = 'branch'
        elif request.user.role == 'branch':
            role = 'staff'
        else:
            messages.error(request, 'You are not authorized to create users.')
            return redirect('user_list')

        new_password = get_random_string(length=8)

        user = CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=contact,
            role=role,
            password=make_password(new_password)
        )

        if request.user.role == 'organization':
            Branch.objects.create(
                name=f"{first_name} {last_name}'s Branch",
                organization=Organization.objects.get(owner=request.user),
                created_by=request.user,
                available_accounts=','.join(available_accounts),
                owner=user
            )
        elif request.user.role == 'branch':
            Staff.objects.create(
                user=user,
                branch=Branch.objects.get(owner=request.user),
                access_accounts=','.join(available_accounts)
            )

        send_mail(
            'Your account has been created',
            f'Your password is: {new_password}',
            'admin@yourdomain.com',
            [user.email],
            fail_silently=False,
        )
        return redirect(reverse('user_list'))

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'

    def form_valid(self, form):
        self.request.user.password_changed = True
        self.request.user.save()
        return JsonResponse({'status': 'success'})

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'errors': form.errors})

@csrf_exempt
def member_search(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        search_text = data.get('SearchText')
        try:
            organization = Organization.objects.get(owner=request.user)
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organization not found'}, status=404)

        api_url = f"{organization.base_url}SearchMemberNameEbank"
        payload = {
            "clientId": organization.clint_id,
            "SearchText": search_text,
            "username": organization.username
        }

        try:
            response = requests.post(api_url, json=payload)
            if response.status_code != 200:
                return JsonResponse({'error': 'Failed to fetch data from external API'}, status=response.status_code)

            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                print("Response content:", response.content)
                return JsonResponse({'error': 'Invalid response from external API'}, status=500)

            if response_data.get('isSuccess'):
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Failed to fetch data from external API'}, status=response.status_code)
        except requests.RequestException as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def member_ledger(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        memb_num = data.get('MembNum')
        try:
            organization = Organization.objects.get(owner=request.user)
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organization not found'}, status=404)

        api_url = f"{organization.base_url}MemberLedgerEbank"
        payload = {
            "clientId": organization.clint_id,
            "Flag": "ALL",
            "MembNum": memb_num,
            "username": organization.username
        }

        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()

            if response.status_code == 200 and response_data.get('isSuccess'):
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Failed to fetch data from external API'}, status=response.status_code)
        except requests.RequestException as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def fetch_member_ledger(request):
    if request.method == 'POST':
        try:
            branch = Branch.objects.get(owner=request.user)
            organization = branch.organization
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Organization not found'}, status=404)

        api_url = f"{organization.base_url}MemberLedgerEbank"
        payload = {
            "clientId": organization.clint_id,
            "Flag": "ALL",
            "MembNum": branch.member_number,
            "username": organization.username
        }

        try:
            response = requests.post(api_url, json=payload)
            response_data = response.json()
            if response.status_code == 200 and response_data.get('isSuccess'):
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Failed to fetch data from external API'}, status=response.status_code)
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
