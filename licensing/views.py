from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.signing import Signer, TimestampSigner
from django.http import HttpResponseBadRequest
from .models import License, Device
import urllib.parse

@login_required
def activate_license(request):
    """
    Handles the activation request from the local device.
    1. Receives key, hwid, callback_url.
    2. Verifies user owns the license key.
    3. Binds the HWID to the license (if slot available).
    4. Redirects back to callback_url with a SIGNED token.
    """
    key = request.GET.get('key')
    hwid = request.GET.get('hwid')
    callback_url = request.GET.get('callback_url') 
    device_name = request.GET.get('name', 'My Smarty Device')

    if not all([key, hwid, callback_url]):
        return render(request, 'licensing/error.html', {'message': "Missing required parameters (key, hwid, callback_url)."})

    try:
        # 1. Verify License exists and belongs to user
        license_obj = License.objects.get(key=key, user=request.user)
        
        if not license_obj.is_active:
             return render(request, 'licensing/error.html', {'message': "This license key has been suspended."})

        # 2. Check/Bind Device
        device, created = Device.objects.get_or_create(
            license=license_obj, 
            hardware_id=hwid,
            defaults={'name': device_name}
        )

        if not created and device.license != license_obj:
             # This HWID is already bound to another license? (Edge case, assuming hwid is unique per machine but not globally unique across all installs without context)
             # For simplicity, we assume Device is tied to License+HWID tuple unique in model.
             pass
        
        # Check limits if it's a new device
        if created:
            current_count = license_obj.devices.count()
            if current_count > license_obj.max_devices:
                device.delete() # Rollback
                return render(request, 'licensing/error.html', {'message': f"License limit reached. Max devices: {license_obj.max_devices}"})

        # 3. Generate Signed Token
        # The token contains: license_id, tier, expiry, hwid.
        # It is signed with the server's SECRET_KEY.
        signer = TimestampSigner()
        data_to_sign = {
            'license_key': license_obj.key,
            'tier': license_obj.tier,
            'hwid': hwid,
            'user': request.user.username,
            'expiry': str(license_obj.expiry_date) if license_obj.expiry_date else 'LIFETIME'
        }
        signed_token = signer.sign_object(data_to_sign)

        # 4. Redirect Back to Local App
        # Construct the redirect URL with the token
        params = urllib.parse.urlencode({'token': signed_token, 'status': 'success'})
        target = f"{callback_url}?{params}"
        
        return redirect(target)

    except License.DoesNotExist:
        return render(request, 'licensing/error.html', {'message': "Invalid license key or does not belong to your account."})
    except Exception as e:
        return render(request, 'licensing/error.html', {'message': f"Activation error: {str(e)}"})
