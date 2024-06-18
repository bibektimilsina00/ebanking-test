from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.crypto import get_random_string
from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import CustomUser
from organizations.models import Organization
from branches.models import Branch
from staff.models import Staff
from django.contrib.auth.hashers import make_password

class UserListView(LoginRequiredMixin, TemplateView):
    template_name = 'user_management/user_list.html'

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
