from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid
from django.utils.timezone import now
from django.conf import settings
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('initiator', 'Initiator'),
        ('reviewer', 'Reviewer'),
        ('approver', 'Approver'),
        ('admin', 'Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    u_name = models.CharField(unique=True,max_length=50)
    email = models.EmailField(unique=True, max_length=254)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='initiator')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 
    USERNAME_FIELD = 'u_name'
    REQUIRED_FIELDS = ['email', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class UserSessionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    token_expiry = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def session_duration(self):
        if self.logout_time:
            return self.logout_time - self.login_time
        return None

    def __str__(self):
        return f"{self.user} session at {self.login_time}"
