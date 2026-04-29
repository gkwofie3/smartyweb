from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from licensing.models import License, Device
import json
import datetime


# ─────────────────────────────────────────────────────────────
# Shared signing helper
# ─────────────────────────────────────────────────────────────

def _sign_activation(license_obj: License, hwid: str) -> str:
    signer = TimestampSigner()
    payload = {
        'license_key': license_obj.key,
        'tier':        license_obj.tier,
        'components':  license_obj.get_components(),
        'hwid':        hwid,
        'max_devices': license_obj.max_devices,
        'expiry':      license_obj.expiry_date.isoformat() if license_obj.expiry_date else 'LIFETIME',
    }
    return signer.sign_object(payload)


def _json_err(msg, status=400):
    return JsonResponse({'error': msg, 'ok': False}, status=status)


# ─────────────────────────────────────────────────────────────
# 1. Check Key  (pre-install, no auth needed)
#    POST /api/licensing/check-key/
#    body: { "key": "SMRT-XXXX-..." }
# ─────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def check_key(request):
    """
    Called by the installer BEFORE extracting any files.
    Validates the key exists, is active, and has device slots available.
    Returns 200 OK or 4xx with a plain-English reason.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return _json_err('Invalid request body.')

    key = (data.get('key') or '').strip().upper()
    if not key:
        return _json_err('License key is required.')

    try:
        lic = License.objects.get(key=key)
    except License.DoesNotExist:
        return _json_err(
            'This license key was not found. Please check you typed it correctly, '
            'or contact Rovid support.',
            status=404
        )

    if not lic.is_active:
        return _json_err(
            'This license key has been suspended. Please contact Rovid support.',
            status=403
        )

    if lic.is_expired():
        return _json_err(
            'This license key has expired. Please renew your subscription at smarty.rovidgh.com.',
            status=403
        )

    # Check device slots
    used = lic.devices.filter(is_revoked=False).count()
    if used >= lic.max_devices:
        return _json_err(
            f'This license is already in use on {used} device(s). '
            f'Your plan allows {lic.max_devices} device(s). '
            'Please deactivate an existing device or upgrade your plan.',
            status=403
        )

    return JsonResponse({
        'ok':         True,
        'tier':       lic.tier,
        'components': lic.get_components(),
        'max_devices': lic.max_devices,
        'expiry':     lic.expiry_date.isoformat() if lic.expiry_date else 'LIFETIME',
    })


# ─────────────────────────────────────────────────────────────
# 2. Activate  (called by smarty.exe --activate <key>)
#    POST /api/licensing/activate/
#    body: { "key": "...", "hwid": "...", "name": "...", "version": "...",
#            "local_ip": "...", "port": 5000 }
# ─────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def activate(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return _json_err('Invalid request body.')

    key     = (data.get('key') or '').strip().upper()
    hwid    = (data.get('hwid') or '').strip()
    name    = data.get('name', 'Smarty Installation')
    version = data.get('version', '')
    local_ip = data.get('local_ip')
    port    = int(data.get('port', 5000))

    if not key or not hwid:
        return _json_err('key and hwid are required.')

    try:
        lic = License.objects.get(key=key)
    except License.DoesNotExist:
        return _json_err('Invalid license key.', status=404)

    if not lic.is_valid():
        return _json_err('License is suspended or expired.', status=403)

    # Get or create device binding
    device, created = Device.objects.get_or_create(
        license=lic,
        hardware_id=hwid,
        defaults={
            'name':     name,
            'local_ip': local_ip,
            'port':     port,
            'version':  version,
        }
    )

    if device.is_revoked:
        return _json_err(
            'This device has been revoked. Please contact Rovid support to re-activate.',
            status=403
        )

    # Slot limit (only check on new devices)
    if created:
        used = lic.devices.filter(is_revoked=False).count()
        if used > lic.max_devices:
            device.delete()
            return _json_err(
                f'Device limit reached ({lic.max_devices} allowed). '
                'Please deactivate another device first.',
                status=403
            )
    else:
        # Update info on re-activation
        if local_ip:
            device.local_ip = local_ip
        device.port    = port
        device.version = version
        device.last_validated = timezone.now()
        device.save()

    signed_token = _sign_activation(lic, hwid)

    return JsonResponse({
        'ok':           True,
        'token':        signed_token,
        'tier':         lic.tier,
        'components':   lic.get_components(),
        'expiry':       lic.expiry_date.isoformat() if lic.expiry_date else 'LIFETIME',
        'max_devices':  lic.max_devices,
        'activated_at': device.activated_at.isoformat(),
    })


# ─────────────────────────────────────────────────────────────
# 3. Validate / Heartbeat  (every 6 hours from running smarty.exe)
#    POST /api/licensing/validate/
#    body: { "key": "...", "hwid": "...", "local_ip": "...", "port": 5000, "version": "..." }
# ─────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def validate(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return _json_err('Invalid request body.')

    key  = (data.get('key') or '').strip().upper()
    hwid = (data.get('hwid') or '').strip()

    if not key or not hwid:
        return _json_err('key and hwid are required.')

    # Pull public IP from request headers
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    public_ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')

    try:
        device = Device.objects.select_related('license').get(
            license__key=key, hardware_id=hwid
        )
    except Device.DoesNotExist:
        return JsonResponse({
            'ok':     False,
            'status': 'UNREGISTERED',
            'error':  'Device not found. Please re-activate.',
        }, status=404)

    lic = device.license

    if device.is_revoked:
        return JsonResponse({'ok': False, 'status': 'REVOKED',
                             'error': 'This device has been revoked.'}, status=403)

    if not lic.is_valid():
        return JsonResponse({'ok': False, 'status': 'EXPIRED',
                             'error': 'License expired or suspended.'}, status=403)

    # Update heartbeat data
    update_fields = ['last_validated', 'public_ip']
    device.last_validated = timezone.now()
    device.public_ip      = public_ip
    if data.get('local_ip'):
        device.local_ip = data['local_ip']
        update_fields.append('local_ip')
    if data.get('version'):
        device.version = data['version']
        update_fields.append('version')
    if data.get('port'):
        device.port = int(data['port'])
        update_fields.append('port')
    device.save(update_fields=update_fields + ['last_checkin'])

    # Re-issue a fresh signed token on every validate call
    signed_token = _sign_activation(lic, hwid)

    return JsonResponse({
        'ok':         True,
        'status':     'ACTIVE',
        'token':      signed_token,
        'components': lic.get_components(),
        'expiry':     lic.expiry_date.isoformat() if lic.expiry_date else 'LIFETIME',
    })


# ─────────────────────────────────────────────────────────────
# 4. Deactivate  (admin revokes or user moves to new machine)
#    POST /api/licensing/deactivate/
#    body: { "key": "...", "hwid": "..." }
# ─────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def deactivate(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return _json_err('Invalid request body.')

    key  = (data.get('key') or '').strip().upper()
    hwid = (data.get('hwid') or '').strip()

    if not key or not hwid:
        return _json_err('key and hwid are required.')

    try:
        device = Device.objects.get(license__key=key, hardware_id=hwid)
        device.is_revoked = True
        device.save(update_fields=['is_revoked'])
        return JsonResponse({'ok': True, 'message': 'Device deactivated successfully.'})
    except Device.DoesNotExist:
        return _json_err('Device not found.', status=404)


# ─────────────────────────────────────────────────────────────
# 5. Status  (GET — for admin dashboard or debugging)
#    GET /api/licensing/status/?hwid=<hwid>
# ─────────────────────────────────────────────────────────────
@require_GET
def status(request):
    hwid = request.GET.get('hwid', '').strip()
    if not hwid:
        return _json_err('hwid required.')

    try:
        device = Device.objects.select_related('license').get(hardware_id=hwid)
    except Device.DoesNotExist:
        return JsonResponse({'ok': False, 'status': 'UNREGISTERED'}, status=404)

    lic = device.license
    return JsonResponse({
        'ok':           True,
        'status':       'REVOKED' if device.is_revoked else ('ACTIVE' if lic.is_valid() else 'EXPIRED'),
        'tier':         lic.tier,
        'components':   lic.get_components(),
        'expiry':       lic.expiry_date.isoformat() if lic.expiry_date else 'LIFETIME',
        'last_checkin': device.last_checkin.isoformat(),
    })


# ─────────────────────────────────────────────────────────────
# 6. Legacy browser-based dashboard (keep for portal users)
#    GET/POST /licensing/activate-device/
# ─────────────────────────────────────────────────────────────
@login_required
def activate_device_page(request):
    """
    Browser-based dashboard: shows the user's licenses and active devices.
    """
    licenses = License.objects.filter(user=request.user).prefetch_related('devices')
    all_components = ['main', 'client', 'editor', 'fbd', 'script', 'sva']
    return render(request, 'licensing/dashboard.html', {
        'licenses': licenses,
        'all_components': all_components
    })

