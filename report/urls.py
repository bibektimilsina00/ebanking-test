from django.urls import path
from .views import ReportView,export_report

urlpatterns = [
    path('', ReportView.as_view(), name='report'),
    path('export/',export_report,name='export_report')
    
]