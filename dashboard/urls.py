from django.urls import path
from .views import OrganizationDashboardView, BranchDashboardView, StaffDashboardView,RedirectDashboardView

urlpatterns = [
    
    path('organization/', OrganizationDashboardView.as_view(), name='organization_dashboard'),
    path('branch/', BranchDashboardView.as_view(), name='branch_dashboard'),
    path('staff/', StaffDashboardView.as_view(), name='staff_dashboard'),
    path("redirect_dashboard/", RedirectDashboardView.as_view(), name="redirect_dashboard")
    
]
