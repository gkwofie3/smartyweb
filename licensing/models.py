from django.db import models
from django.utils import timezone
import uuid

from django.conf import settings

class PricingTier(models.TextChoices):
    LITE = 'LITE', 'Lite (Ordinary)'
    PRO = 'PRO', 'Pro (Connected)'
    ENTERPRISE = 'ENTERPRISE', 'Enterprise (Standard)'

from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid

class PricingTier(models.TextChoices):
    LITE = 'LITE', 'Lite (Ordinary)'
    PRO = 'PRO', 'Pro (Connected)'
    ENTERPRISE = 'ENTERPRISE', 'Enterprise (Standard)'

class License(models.Model):
    """
    Represents a product key purchased by a customer.
    Admin generates this and assigns it to a user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='licenses')
    key = models.CharField(max_length=100, unique=True, help_text="The license key string (e.g. SMARTY-XXXX-YYYY)")
    tier = models.CharField(max_length=20, choices=PricingTier.choices, default=PricingTier.LITE)
    max_devices = models.IntegerField(default=1, help_text="Number of devices allowed on this license")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.key} ({self.tier}) - {self.user.username}"

class Device(models.Model):
    """
    Represents a physical hardware instance activated against a license.
    """
    license = models.ForeignKey(License, on_delete=models.CASCADE, related_name='devices')
    hardware_id = models.CharField(max_length=255, help_text="Unique Hardware ID of the local machine")
    name = models.CharField(max_length=255, help_text="Friendly name for this device (e.g. Factory Floor 1)")
    
    # Connectivity Info
    local_ip = models.GenericIPAddressField(null=True, blank=True, protocol='both', help_text="Local Network IP")
    public_ip = models.GenericIPAddressField(null=True, blank=True, protocol='both', help_text="Public WAN IP (optional)")
    port = models.IntegerField(default=8000, help_text="Local Port")
    version = models.CharField(max_length=50, blank=True, null=True, help_text="Smarty Version")

    activated_at = models.DateTimeField(auto_now_add=True)
    last_checkin = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('license', 'hardware_id')

    def __str__(self):
        return f"{self.name} ({self.hardware_id})"
