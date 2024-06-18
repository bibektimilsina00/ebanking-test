from django.contrib import admin
from . models import Staff

# Register your models here.
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'created_at', 'updated_at')
    search_fields = ('user__username', 'branch__name')