"""
views.py — Paystack payment views.

Endpoints:
  GET  /payment/checkout/?plan=PRO  → checkout page (login required)
  POST /payment/verify/             → verify after Paystack callback
  POST /payment/webhook/paystack/   → server-to-server webhook (CSRF exempt)
  GET  /payment/success/            → show license key to user
  GET  /payment/cancel/             → friendly cancel page
"""

import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Order
from .services import (
    create_license_for_order,
    usd_to_ghs_pesewas,
    verify_paystack_payment,
    verify_webhook_signature,
)

logger = logging.getLogger(__name__)

# Plan metadata displayed on the checkout page
PLAN_META = {
    'LITE': {
        'label':       'Smarty Lite',
        'usd_amount':  1800,
        'period':      'one-time / lifetime',
        'features':    ['Smarty Manager', '1 device', 'Standard support'],
        'is_annual':   False,
    },
    'PRO': {
        'label':       'Smarty Pro',
        'usd_amount':  4500,
        'period':      'per year',
        'features':    ['Manager + Client + Editor', 'Up to 3 devices', 'Priority support'],
        'is_annual':   True,
    },
    'ENTERPRISE': {
        'label':       'Smarty Enterprise',
        'usd_amount':  8500,
        'period':      'per year',
        'features':    ['All 6 components', 'Up to 10 devices', 'Dedicated support + SLA'],
        'is_annual':   True,
    },
}


# ── GET /payment/checkout/?plan=PRO ──────────────────────────

@login_required
def checkout(request):
    plan = request.GET.get('plan', '').upper()

    if plan not in PLAN_META:
        return render(request, 'payment/error.html', {
            'message': 'Invalid plan selected. Please choose a plan from our pricing page.'
        })

    meta      = PLAN_META[plan]
    usd_cents = meta['usd_amount']  # stored as whole dollars on display
    from decimal import Decimal
    ghs, rate, pesewas = usd_to_ghs_pesewas(Decimal(str(usd_cents)))

    # Create a pending Order (idempotent — check if user already has one in progress)
    order = Order.objects.create(
        user         = request.user,
        email        = request.user.email,
        plan         = plan,
        usd_amount   = usd_cents,
        ghs_amount   = ghs,
        ghs_pesewas  = pesewas,
        exchange_rate= rate,
    )

    callback_url = f'{settings.SITE_URL}/payment/verify/?reference={order.reference}'

    return render(request, 'payment/checkout.html', {
        'order':          order,
        'plan':           plan,
        'meta':           meta,
        'ghs_amount':     ghs,
        'exchange_rate':  rate,
        'pesewas':        pesewas,
        'callback_url':   callback_url,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    })


# ── GET /payment/verify/ ──────────────────────────────────────
# Called when Paystack inline popup completes (via JS redirect)

@login_required
def verify(request):
    reference = request.GET.get('reference') or request.POST.get('reference')
    if not reference:
        return render(request, 'payment/error.html', {
            'message': 'No payment reference provided.'
        })

    order = get_object_or_404(Order, reference=reference)

    # Prevent re-processing already paid orders
    if order.status == Order.STATUS_PAID and order.license_id:
        return redirect(f'/payment/success/?reference={reference}')

    data = verify_paystack_payment(reference)

    if not data:
        order.status = Order.STATUS_FAILED
        order.save(update_fields=['status'])
        return render(request, 'payment/cancel.html', {
            'order':   order,
            'reason':  'Payment could not be verified with Paystack. If money was deducted, please contact support.'
        })

    # Store Paystack transaction ID
    order.paystack_id = data.get('id') or data.get('reference')
    order.save(update_fields=['paystack_id'])

    # Create license
    license = create_license_for_order(order)
    if not license:
        return render(request, 'payment/error.html', {
            'message': 'Payment received but license creation failed. Our team has been notified and will issue your key shortly.'
        })

    return redirect(f'/payment/success/?reference={reference}')


# ── POST /payment/webhook/paystack/ ───────────────────────────
# Server-to-server backup — CSRF exempt

@csrf_exempt
def paystack_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    payload   = request.body
    signature = request.headers.get('X-Paystack-Signature', '')

    if not verify_webhook_signature(payload, signature):
        logger.warning('[Webhook] Invalid Paystack signature — rejected')
        return HttpResponse('Invalid signature', status=401)

    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return HttpResponse('Bad JSON', status=400)

    if event.get('event') != 'charge.success':
        return HttpResponse('OK', status=200)  # Ignore other events

    reference = event['data'].get('reference')
    if not reference:
        return HttpResponse('OK', status=200)

    try:
        order = Order.objects.get(reference=reference)
    except Order.DoesNotExist:
        logger.warning(f'[Webhook] Order not found for reference {reference}')
        return HttpResponse('OK', status=200)

    if order.status != Order.STATUS_PAID:
        create_license_for_order(order)

    return HttpResponse('OK', status=200)


# ── GET /payment/success/ ────────────────────────────────────

@login_required
def success(request):
    reference = request.GET.get('reference')
    order     = get_object_or_404(Order, reference=reference, user=request.user)

    if order.status != Order.STATUS_PAID:
        return render(request, 'payment/error.html', {
            'message': 'This order has not been completed. Please contact support if you believe this is an error.'
        })

    return render(request, 'payment/success.html', {
        'order':   order,
        'license': order.license,
    })


# ── GET /payment/cancel/ ─────────────────────────────────────

def cancel(request):
    reference = request.GET.get('reference', '')
    order     = None
    if reference:
        try:
            order = Order.objects.get(reference=reference)
            if order.status == Order.STATUS_PENDING:
                order.status = Order.STATUS_FAILED
                order.save(update_fields=['status'])
        except Order.DoesNotExist:
            pass

    return render(request, 'payment/cancel.html', {'order': order})
