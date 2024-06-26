from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from django_cryptography.fields import encrypt


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email =  (models.EmailField(unique=True))
    phone = encrypt(models.CharField(max_length=15, blank=True))
    first_name = encrypt(models.CharField(max_length=30, blank=True))
    last_name = encrypt(models.CharField(max_length=30, blank=True))
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    password_changed = models.BooleanField(default=False)
    username =  models.CharField(max_length=30, blank=True,null=True)

    ROLE_CHOICES = [
        ('superadmin', 'SuperAdmin'),
        ('organization', 'Organization'),
        ('branch', 'Branch'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
