from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models

import uuid
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)  # Superusers must have is_staff=True
        extra_fields.setdefault('is_superuser', True)  # Superusers must have is_superuser=True
        extra_fields.setdefault('role', 'Admin')

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
        ('Volunteer', 'Volunteer'),

    ]
    
    COUNTRY_CHOICES = [
        ('India', 'India'),
        ('USA', 'USA'),
        ('UK', 'UK'),
        ('Canada', 'Canada'),
        ('Australia', 'Australia'),
        ('Germany', 'Germany'),
        ('France', 'France'),
        ('Japan', 'Japan'),
        ('China', 'China'),
        ('Brazil', 'Brazil'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')
    location = models.CharField(max_length=100, default='unknown')
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    reports = models.IntegerField(default=0)     # Number of reports made by the volunteer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']  # Fields required for creating superuser

    def save(self, *args, **kwargs):
        if self.role == 'Admin':
            self.is_admin = True
            self.is_staff = True
            self.location = 'unknown'  # Ensure location is 'unknown' for Admins
        elif self.role == 'User':
            self.is_admin = False
            self.is_staff = False
            self.location = 'unknown'  # Ensure location is 'unknown' for Users
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email




class UserToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='token')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token}"