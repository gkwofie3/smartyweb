from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class TwoFAMethod(models.TextChoices):
    NONE = 'NONE', 'None'
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'

class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    two_fa_method = models.CharField(max_length=10, choices=TwoFAMethod.choices, default=TwoFAMethod.NONE)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.username

class VerificationCode(models.Model):
    CODE_TYPES = [
        ('EMAIL', 'Email Verification'),
        ('PHONE', 'Phone Verification'),
        ('2FA', 'Two-Factor Auth'),
        ('PWD', 'Password Reset'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    code_type = models.CharField(max_length=10, choices=CODE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        # Valid for 15 minutes
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < 900
