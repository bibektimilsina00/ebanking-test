from django.contrib import admin
from .models import Organization, Branch, Staff, Theme
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser,Account
from .forms import UserCreationForm, UserChangeForm

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'role', 'is_active', 'first_name', 'last_name','password_changed')
    list_filter = ('is_active', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ( 'is_active', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    
    
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_holder', 'account_number', 'balance', 'created_at', 'updated_at')
    search_fields = ('account_holder__email', 'account_number')
    list_filter = ('created_at', 'updated_at')

admin.site.register(CustomUser, UserAdmin)

admin.site.register(Account, AccountAdmin)

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_by', 'created_at', 'updated_at')
    search_fields = ('name', 'organization__name')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'created_at', 'updated_at')
    search_fields = ('user__username', 'branch__name')

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'organization__name')


