from django.db import models
from accounts.models import CustomUser

class Organization(models.Model):
    name = models.CharField(max_length=255)
    base_url = models.CharField(max_length=255, blank=True)
    clint_id = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(CustomUser, related_name='created_organizations', on_delete=models.CASCADE, limit_choices_to={'role': 'superadmin'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(CustomUser, related_name='organizations', on_delete=models.CASCADE, limit_choices_to={'role': 'organization'}, blank=True, null=True)

    def __str__(self):
        return self.name
