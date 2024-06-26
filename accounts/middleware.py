from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

class PasswordChangeMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure the user attribute is present and user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Check if the password change is required and the user is not already on the change password page
            if not request.user.password_changed and not request.path.startswith(reverse('password_change')):
                # Redirect to the password change form unless it's a safe path
                return redirect('password_change')
        
        # Continue processing the request if no conditions are met
        response = self.get_response(request)
        return response
