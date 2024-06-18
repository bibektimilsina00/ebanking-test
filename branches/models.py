from django.db import models
from organizations.models import Organization
from accounts.models import CustomUser

class Branch(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, related_name='branches', on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, related_name='created_branches', on_delete=models.CASCADE, limit_choices_to={'role': 'organization'})
    available_accounts = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(CustomUser, related_name='branches', on_delete=models.CASCADE, limit_choices_to={'role': 'branch'}, blank=True, null=True)
    member_number = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
