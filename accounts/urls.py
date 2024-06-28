from django.urls import path
from .views import member_search, member_ledger, fetch_member_ledger,ProfileView

urlpatterns = [
    path('member-search/', member_search, name='member_search'),
    path('member-ledger/', member_ledger, name='member_ledger'),
    path('fetch-member-ledger/', fetch_member_ledger, name='fetch_member_ledger'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
]
