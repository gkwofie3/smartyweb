"""
services.py — Payment processing services.

1. USD → GHS live conversion (frankfurter.app API, 1-hour in-memory cache)
2. Paystack payment verification
3. Automatic license creation after successful payment
4. License key email delivery
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import timedelta
from decimal import Decimal

import requests
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# ── Currency conversion cache ─────────────────────────────────
_fx_cache = {'rate': None, 'fetched_at': 0}
_FX_TTL   = 3600  # 1 hour


def get_usd_to_ghs_rate() -> Decimal:
    """
    Fetches live USD → GHS exchange rate from frankfurter.app.
    Caches the result for 1 hour. Falls back to a conservative
    default (16.0) if the API is unreachable.
    """
    now = time.time()
    if _fx_cache['rate'] and (now - _fx_cache['fetched_at']) < _FX_TTL:
        return _fx_cache['rate']

    try:
        r = requests.get(
            'https://api.frankfurter.app/latest?from=USD&to=GHS',
            timeout=8
        )
        data = r.json()
        rate = Decimal(str(data['rates']['GHS']))
        _fx_cache['rate']       = rate
        _fx_cache['fetched_at'] = now
        logger.info(f'[FX] USD→GHS rate updated: {rate}')
        return rate
    except Exception as e:
        logger.warning(f'[FX] Could not fetch rate: {e} — using cached/default')
        return _fx_cache['rate'] or Decimal('16.00')  # conservative fallback


def usd_to_ghs_pesewas(usd_amount: Decimal) -> tuple[Decimal, Decimal, int]:
    """
    Convert USD amount to GHS and return:
      (ghs_decimal, exchange_rate, pesewas_int)
    """
    rate      = get_usd_to_ghs_rate()
    ghs       = (usd_amount * rate).quantize(Decimal('0.01'))
    pesewas   = int(ghs * 100)
    return ghs, rate, pesewas


# ── Paystack API ──────────────────────────────────────────────

PAYSTACK_BASE = 'https://api.paystack.co'


def _ps_headers():
    return {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type':  'application/json',
    }


def verify_paystack_payment(reference: str) -> dict | None:
    """
    Calls Paystack's verify endpoint. Returns the `data` dict on success,
    None on failure.
    """
    try:
        r = requests.get(
            f'{PAYSTACK_BASE}/transaction/verify/{reference}',
            headers=_ps_headers(),
            timeout=15
        )
        body = r.json()
        if body.get('status') and body['data']['status'] == 'success':
            return body['data']
        logger.warning(f'[Paystack] Verify failed for {reference}: {body}')
        return None
    except Exception as e:
        logger.error(f'[Paystack] Verify error for {reference}: {e}')
        return None


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Paystack webhook HMAC-SHA512 signature."""
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


# ── License creation ──────────────────────────────────────────

PLAN_CONFIG = {
    'LITE': {
        'components':    ['main'],
        'duration_days': None,   # perpetual
        'max_devices':   1,
    },
    'PRO': {
        'components':    ['main', 'client', 'editor'],
        'duration_days': 365,
        'max_devices':   3,
    },
    'ENTERPRISE': {
        'components':    ['main', 'client', 'editor', 'fbd', 'script', 'sva'],
        'duration_days': 365,
        'max_devices':   10,
    },
}


def create_license_for_order(order) -> 'licensing.License | None':
    """
    Idempotent — safe to call multiple times (webhook + redirect race).
    Returns the (possibly existing) license, or None on error.
    """
    from licensing.models import License

    # Already created (race condition guard)
    if order.license_id:
        return order.license

    plan   = order.plan
    config = PLAN_CONFIG.get(plan, PLAN_CONFIG['LITE'])

    expiry = None
    if config['duration_days']:
        expiry = timezone.now() + timedelta(days=config['duration_days'])

    try:
        lic = License.objects.create(
            user        = order.user,
            tier        = plan,
            components  = config['components'],
            max_devices = config['max_devices'],
            expiry_date = expiry,
            notes       = f'Auto-created from order {order.reference}',
        )
        order.license = lic
        order.status  = 'PAID'
        order.paid_at = timezone.now()
        order.save(update_fields=['license', 'status', 'paid_at'])

        # Send email
        send_license_email(order.email, lic, order)
        return lic

    except Exception as e:
        logger.error(f'[License] Failed to create license for order {order.reference}: {e}')
        return None


# ── Email delivery ────────────────────────────────────────────

def send_license_email(email: str, license, order):
    """Send the license key to the customer via email."""
    plan_config = PLAN_CONFIG.get(order.plan, {})

    subject = f'Your Smarty {order.get_plan_display()} License Key – Rovid Smart Technologies'

    context = {
        'license_key':  license.key,
        'tier':         order.get_plan_display(),
        'components':   license.get_components(),
        'max_devices':  license.max_devices,
        'expiry':       license.expiry_date.strftime('%d %B %Y') if license.expiry_date else 'Lifetime / Perpetual',
        'is_perpetual': license.expiry_date is None,
        'order_ref':    order.reference,
        'usd_amount':   order.usd_amount,
        'download_url': f'{settings.SITE_URL}/downloads/',
        'portal_url':   f'{settings.SITE_URL}/licensing/activate-device/',
        'support_url':  f'{settings.SITE_URL}/contact/',
    }

    text_body = render_to_string('email/license_key.txt', context)
    html_body = render_to_string('email/license_key.html', context)

    msg = EmailMultiAlternatives(
        subject   = subject,
        body      = text_body,
        from_email= settings.DEFAULT_FROM_EMAIL,
        to        = [email],
        reply_to  = [settings.ADMIN_NOTIFICATION_EMAIL],
    )
    msg.attach_alternative(html_body, 'text/html')
    
    # Use explicit connection with timeout
    from django.core.mail import get_connection
    connection = get_connection(timeout=10)
    msg.connection = connection

    try:
        msg.send(fail_silently=False)
        logger.info(f'[Email] License key sent to {email} for order {order.reference}')
    except Exception as e:
        logger.error(f'[Email] Failed to send to {email}: {e}')
        if "Connection unexpectedly closed" in str(e):
             logger.error("SMTP connection was closed prematurely. Check your Gmail App Password.")

    # Notify admin
    try:
        from django.core.mail import send_mail
        send_mail(
            subject      = f'[Rovid] New license sale: {order.plan} — {order.reference}',
            message      = f'Order: {order.reference}\nPlan: {order.plan}\nEmail: {email}\nAmount: ${order.usd_amount} USD (GHS {order.ghs_amount})',
            from_email   = settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass
