from django.urls import path
from .views import CustomLoginView, CustomPasswordChangeView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
]
