from django.urls import path
from .views import (
    CustomLoginView,
    OrganizationDashboardView,
    BranchDashboardView,
    StaffDashboardView,
    RedirectDashboardView,
    UserListView,
    ResetPasswordView,
    SuspendUserView,
    ActivateUserView,
    CreateUserView,
    CustomPasswordChangeView,
    member_search,
    member_ledger,
    fetch_member_ledger
    
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "redirect_dashboard/",
        RedirectDashboardView.as_view(),
        name="redirect_dashboard",
    ),
    path(
        "organization/",
        OrganizationDashboardView.as_view(),
        name="organization_dashboard",
    ),
    path("branch/", BranchDashboardView.as_view(), name="branch_dashboard"),
    path("staff/", StaffDashboardView.as_view(), name="staff_dashboard"),
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("suspend-user/", SuspendUserView.as_view(), name="suspend_user"),
    path("activate-user/", ActivateUserView.as_view(), name="activate_user"),
    path("create-user/", CreateUserView.as_view(), name="create_user"),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('member-search/', member_search, name='member_search'),
    
    path('member-ledger/', member_ledger, name='member_ledger'),
    path('fetch-member-ledger/', fetch_member_ledger, name='fetch_member_ledger'),
]
