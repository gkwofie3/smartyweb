from django.db import models
from django.conf import settings
import uuid


class Order(models.Model):

    STATUS_PENDING  = 'PENDING'
    STATUS_PAID     = 'PAID'
    STATUS_FAILED   = 'FAILED'
    STATUS_REFUNDED = 'REFUNDED'

    STATUS_CHOICES = [
        (STATUS_PENDING,  'Pending'),
        (STATUS_PAID,     'Paid'),
        (STATUS_FAILED,   'Failed / Cancelled'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    PLAN_CHOICES = [
        ('LITE',       'Smarty Lite'),
        ('PRO',        'Smarty Pro'),
        ('ENTERPRISE', 'Smarty Enterprise'),
    ]

    # ── Identity ───────────────────────────────────────────────
    reference  = models.CharField(
        max_length=64, unique=True, editable=False,
        help_text='Paystack payment reference (also used as order ID)'
    )
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders'
    )
    email      = models.EmailField(help_text='Email at time of purchase (denormalised)')

    # ── Plan ───────────────────────────────────────────────────
    plan       = models.CharField(max_length=20, choices=PLAN_CHOICES)

    # ── Amounts ────────────────────────────────────────────────
    usd_amount    = models.DecimalField(max_digits=10, decimal_places=2,
                                        help_text='Displayed price in USD')
    ghs_amount    = models.DecimalField(max_digits=12, decimal_places=2,
                                        help_text='Charged amount in GHS')
    ghs_pesewas   = models.BigIntegerField(help_text='Amount sent to Paystack (GHS × 100)')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4,
                                        help_text='USD→GHS rate used at checkout')

    # ── Paystack ───────────────────────────────────────────────
    paystack_id   = models.CharField(max_length=128, blank=True, null=True,
                                     help_text='Paystack transaction ID')

    # ── Status ─────────────────────────────────────────────────
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                  default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at    = models.DateTimeField(null=True, blank=True)

    # ── Result ─────────────────────────────────────────────────
    license    = models.OneToOneField(
        'licensing.License', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='order',
        help_text='Auto-created after successful payment'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'

    def __str__(self):
        return f'{self.reference} [{self.plan}] {self.status} – {self.email}'

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f'SMRT-{uuid.uuid4().hex[:16].upper()}'
        super().save(*args, **kwargs)
