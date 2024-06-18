from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from accounts.manager import CustomUserManager

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone= models.CharField(max_length=15, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    address= models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    password_changed = models.BooleanField(default=False)

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
        return  f"{self.first_name}" + " " + f"{self.last_name}"
    
    
    
    
    
    

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

class Staff(models.Model):
    user = models.OneToOneField(CustomUser, related_name='staff_profile', on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, related_name='staff_members', on_delete=models.CASCADE)
    access_accounts = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return  f"{self.user.first_name}" + " " + f"{self.user.last_name}"

class Theme(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey(Organization, related_name='themes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Account(models.Model):
    account_type = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    account_code= models.CharField(max_length=255)
    account_holder = models.ForeignKey(CustomUser, related_name='accounts', on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, related_name='created_accounts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account_number