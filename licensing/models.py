from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
import secrets
import string


class PricingTier(models.TextChoices):
    LITE       = 'LITE',       'Smarty Lite'
    PRO        = 'PRO',        'Smarty Pro'
    ENTERPRISE = 'ENTERPRISE', 'Smarty Enterprise'


# Components that can be individually licensed
COMPONENT_CHOICES = [
    ('main',   'Smarty Manager (Main)'),
    ('client', 'Smarty Client'),
    ('editor', 'Smarty Editor'),
    ('fbd',    'Smarty FBD Program'),
    ('script', 'Smarty Script Editor'),
    ('sva',    'Smarty Voice Assistant'),
]

# Components bundled per tier
TIER_COMPONENTS = {
    PricingTier.LITE:       ['main'],
    PricingTier.PRO:        ['main', 'client', 'editor'],
    PricingTier.ENTERPRISE: ['main', 'client', 'editor', 'fbd', 'script', 'sva'],
}


def _generate_key():
    """Generate a SMRT-XXXX-XXXX-XXXX-XXXX style license key."""
    chars = string.ascii_uppercase + string.digits
    parts = ['SMRT'] + [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
    return '-'.join(parts)


class License(models.Model):
    """
    A product key purchased by a customer and managed by the Rovid admin.
    Supports per-component licensing and online activation via signed tokens.
    """
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='licenses'
    )
    key         = models.CharField(
        max_length=64, unique=True, default=_generate_key,
        help_text="License key (e.g. SMRT-XXXX-XXXX-XXXX-XXXX)"
    )
    tier        = models.CharField(
        max_length=20, choices=PricingTier.choices, default=PricingTier.LITE
    )
    # Explicit component list — overrides tier defaults when set
    components  = models.JSONField(
        default=list, blank=True,
        help_text="List of component IDs licensed. Leave empty to use tier defaults."
    )
    max_devices = models.IntegerField(default=1)
    is_active   = models.BooleanField(default=True)
    notes       = models.TextField(blank=True, help_text="Internal admin notes")
    created_at  = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Leave blank for perpetual/lifetime license"
    )

    def get_components(self):
        """Return the effective component list (explicit or tier-default)."""
        if self.components:
            return list(self.components)
        return list(TIER_COMPONENTS.get(self.tier, ['main']))

    def is_expired(self):
        if self.expiry_date is None:
            return False
        return timezone.now() > self.expiry_date

    def is_valid(self):
        return self.is_active and not self.is_expired()

    def __str__(self):
        return f"{self.key} [{self.tier}] – {self.user.username}"


class Device(models.Model):
    """
    A physical machine activated against a license.
    Tracks heartbeat, IP, version, and revocation state.
    """
    license     = models.ForeignKey(License, on_delete=models.CASCADE, related_name='devices')
    hardware_id = models.CharField(max_length=255)
    name        = models.CharField(max_length=255, default='Smarty Installation')

    # Network
    local_ip    = models.GenericIPAddressField(null=True, blank=True, protocol='both')
    public_ip   = models.GenericIPAddressField(null=True, blank=True, protocol='both')
    port        = models.IntegerField(default=5000)
    version     = models.CharField(max_length=50, blank=True, null=True)

    # Lifecycle
    activated_at    = models.DateTimeField(auto_now_add=True)
    last_checkin    = models.DateTimeField(auto_now=True)
    last_validated  = models.DateTimeField(null=True, blank=True)
    is_revoked      = models.BooleanField(default=False, help_text="Revoke to force re-activation")

    class Meta:
        unique_together = ('license', 'hardware_id')

    def __str__(self):
        return f"{self.name} [{self.hardware_id[:16]}...]"

