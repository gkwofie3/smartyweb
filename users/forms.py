from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from .models import User

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account found with this email address.")
        return email
