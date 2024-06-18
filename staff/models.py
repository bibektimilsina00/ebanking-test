from django.db import models
from accounts.models import CustomUser
from branches.models import Branch

class Staff(models.Model):
    user = models.OneToOneField(CustomUser, related_name='staff_profile', on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name='staff_members', on_delete=models.CASCADE)
    access_accounts = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
