from django.contrib import admin
from .models import Branch

# Register your models here.
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_by', 'created_at', 'updated_at')
    search_fields = ('name', 'organization__name')