from django.urls import path
from .views import CustomLoginView, CustomPasswordChangeView,root_redirect

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('', root_redirect, name='root'),
]
