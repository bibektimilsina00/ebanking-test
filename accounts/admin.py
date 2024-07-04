from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser
from .forms import UserCreationForm, UserChangeForm

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'role', 'is_active', 'first_name', 'last_name','password_changed','is_staff','avtar')
    list_filter = ('is_active', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'address', 'phone', 'avtar','username')}),
        ('Permissions', {'fields': ( 'is_active', 'groups', 'user_permissions', 'is_staff')}),
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username','role', 'password1', 'password2', 'is_active','is_staff','avtar',)}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    
    
admin.site.register(CustomUser, UserAdmin)

 







 


