from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import CustomUser



from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def root_redirect(request):
    if request.user.is_authenticated:
        
        if request.user.role == "organization":
            return redirect('organization_dashboard')
        elif request.user.role == "branch":
            return redirect('branch_dashboard')
        else:
            return redirect('staff_dashboard')  
    else:
        return redirect('login')


class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'

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

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'authentication/password_change.html'

    def form_valid(self, form):
        self.request.user.password_changed = True
        self.request.user.save()
        return JsonResponse({'status': 'success'})

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'errors': form.errors})
