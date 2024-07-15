from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.forms import ValidationError
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
from django.views.decorators.http import require_POST


from django.db.models import Q


class UserListView(LoginRequiredMixin, TemplateView):
    template_name = "user_management/user_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        search_query = self.request.GET.get("search", "")

        if current_user.role == "organization":
            branches = Branch.objects.filter(created_by=current_user)
            created_account_users = CustomUser.objects.filter(branches__in=branches)
        elif current_user.role == "branch":
            branches = Branch.objects.filter(owner=current_user)
            created_account_users = CustomUser.objects.filter(
                staff_profile__branch__in=branches
            )

            active_staff = CustomUser.objects.filter(
                staff_profile__branch__in=branches, is_active=True
            ).distinct()
            inactive_staff = CustomUser.objects.filter(
                staff_profile__branch__in=branches, is_active=False
            ).distinct()
            context["active_staff"] = active_staff
            context["inactive_staff"] = inactive_staff
        else:
            created_account_users = CustomUser.objects.none()

        # Applying search filter
        if search_query:
            created_account_users = created_account_users.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
            )

        context["users"] = created_account_users.distinct()
        return context


class ResetPasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")

        org_user = CustomUser.objects.filter(role="organization")
        org_data = org_user.first()

        try:
            user = CustomUser.objects.get(id=user_id)
            new_password = get_random_string(length=8)
            user.set_password(new_password)
            user.save()
            send_mail(
                "Your E-Banking Password Has Been Reset",
                f"Dear {user.first_name} {user.last_name},\n\n"
                "We wanted to inform you that your password has been successfully reset. "
                "Below is your new password:\n\n"
                f"Password: {new_password}\n\n"
                "For your security, please log in to your account at your earliest convenience and change your password.\n\n"
                "If you have any questions or require further assistance, please do not hesitate to contact us at:\n"
                f"Phone: {org_data.phone}\n"
                f"Email: {org_data.email}\n\n"
                "Thank you for choosing Finman E-Banking.\n\n"
                "Best regards,\n"
                "The  E-Banking Team",
                [user.email],
                fail_silently=False,
            )

            return JsonResponse(
                {"status": "success", "message": "Password reset and email sent."}
            )
        except CustomUser.DoesNotExist:
            return HttpResponseBadRequest("User does not exist")


class SuspendUserView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return JsonResponse(
                {"status": "success", "message": "User suspended successfully."}
            )
        except CustomUser.DoesNotExist:
            return HttpResponseBadRequest("User does not exist")


class ActivateUserView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return JsonResponse(
                {"status": "success", "message": "User activated successfully."}
            )
        except CustomUser.DoesNotExist:
            return HttpResponseBadRequest("User does not exist")


class DeleteUserView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get("user_id")
        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return JsonResponse(
                {"status": "success", "message": "User deleted successfully."}
            )
        except CustomUser.DoesNotExist:
            return HttpResponseBadRequest("User does not exist")


class CreateUserView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        contact = request.POST.get("contact")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        available_accounts = request.POST.getlist("accounts")
        username = request.POST.get("username")
        member_number = request.POST.get("member-number")

        if request.user.role == "organization":
            role = "branch"
        elif request.user.role == "branch":
            role = "staff"
        else:
            messages.error(request, "You are not authorized to create users.")
            return redirect("user_list")

        new_password = get_random_string(length=8)

        new_user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=contact,
            role=role,
            username=username,
        )
        new_user.set_password(new_password)
        try:
            org_user = CustomUser.objects.filter(role="organization")
            org_data = org_user.first()
            new_user.full_clean()
            new_user.save()
            send_mail(
                "Your E-Banking Password Has Been Reset",
                f"Dear {new_user.first_name} {new_user.last_name},\n\n"
                "We wanted to inform you that your password has been successfully reset. "
                "Below is your new password:\n\n"
                f"Password: {new_password}\n\n"
                "For your security, please log in to your account at your earliest convenience and change your password.\n\n"
                "If you have any questions or require further assistance, please do not hesitate to contact us at:\n"
                f"Phone: {org_data.phone}\n"
                f"Email: {org_data.email}\n\n"
                "Thank you for choosing Finman E-Banking.\n\n"
                "Best regards,\n"
                "The  E-Banking Team",
                [new_user.email],
                fail_silently=False,
            )

        except (ValidationError, IntegrityError) as e:
            return JsonResponse({"status": "error", "message": str(e)})

        if request.user.role == "organization":
            Branch.objects.create(
                name=f"{first_name} {last_name}'s Branch",
                organization=Organization.objects.get(owner=request.user),
                created_by=request.user,
                available_accounts=",".join(available_accounts),
                owner=new_user,
                member_number=member_number,
            )
        elif request.user.role == "branch":
            Staff.objects.create(
                user=new_user,
                branch=Branch.objects.get(owner=request.user),
                access_accounts=",".join(available_accounts),
            )
            org_user = CustomUser.objects.filter(role="organization")
            org_data = org_user.first()

            send_mail(
                "Welcome to E-Banking",
                f"Dear {first_name} {last_name},\n\n"
                "We are pleased to inform you that your account has been successfully created on E-Banking. "
                "Below are your account details:\n\n"
                f"Username: {username}\n"
                f"Password: {new_password}\n\n"
                "For your security, please log in to your account at your earliest convenience and change your password.\n\n"
                "If you have any questions or require further assistance, please do not hesitate to contact us at:\n"
                f"Phone: {org_data.phone}\n"
                f"Email: {org_data.email}\n\n"
                "Thank you for choosing E-Banking.\n\n"
                "Best regards,\n"
                "The E-Banking Team",
                [email],
                fail_silently=False,
            )

        return redirect(reverse("user_list"))


from django.contrib.auth.decorators import login_required


@login_required
def get_user_info(request, user_id):
    try:
        user = CustomUser.objects.get(pk=user_id)

        account_numbers = []
        member_number = None
        branches = user.branches.all()

        member_number = branches[0].member_number

        if user.role == "branch":
            branches = user.branches.all().values("available_accounts")
            account_numbers = [
                account.strip()
                for branch in branches
                for account in branch["available_accounts"].split(",")
                if branch["available_accounts"]
            ]

        elif user.role == "staff":
            staff_profile = user.staff_profile
            if staff_profile and staff_profile.access_accounts:
                account_numbers = [
                    account.strip()
                    for account in staff_profile.access_accounts.split(",")
                ]
        data = {
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "username": user.username,
            "last_name": user.last_name,
            "address": user.address,
            "available_accounts": account_numbers,
            "member_number": member_number,
        }

        return JsonResponse({"status": "success", "data": data})
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "User not found"}, status=404
        )


@login_required
@require_POST
def update_user(request, user_id):

    print(user_id)
    # Attempt to retrieve the user from the database.
    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "User not found"}, status=404
        )

    # Update general user information.
    user.email = request.POST.get(
        "email", user.email
    )  # Use existing value if not provided
    user.phone = request.POST.get(
        "phone", user.phone
    )  # Use existing value if not provided
    user.first_name = request.POST.get(
        "first_name", user.first_name
    )  # Use existing value if not provided
    user.last_name = request.POST.get(
        "last_name", user.last_name
    )  # Use existing value if not provided
    user.address = request.POST.get(
        "address", user.address
    )  # Use existing value if not provided
    user.username = request.POST.get(
        "username", user.username
    )  # Use existing value if not provided

    # Update role-specific information.
    accounts = request.POST.getlist("accounts")  # Fetch the list of accounts

    print(accounts)

    if user.role == "branch":
        # Update all branches associated with this user.
        for branch in user.branches.all():
            branch.available_accounts = ",".join(accounts)
            branch.save()
    elif user.role == "staff":
        # Update all staff profiles associated with this user.
        staff = (
            user.staff_profile
        )  # Assuming there is a related_name='staff_profile' in the Staff model.
        staff.access_accounts = ",".join(accounts)
        staff.save()

    # Save the updated user information.
    user.save()

    return redirect(reverse("user_list"))
