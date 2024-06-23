# models.py

from django.db import models
from accounts.models import CustomUser
from organizations.models import Organization

class ReportViewModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} viewed at {self.viewed_at}"
