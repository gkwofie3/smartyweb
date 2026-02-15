from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from licensing.models import Device, License
import json

def resolve_connection(request):
    """
    Endpoint for Mobile App to find the local SCADA IP/Hostname.
    Expects 'key' (License Key) or 'device_id'.
    """
    key = request.GET.get('key')
    
    if not key:
        return JsonResponse({'error': 'License key required'}, status=400)
    
    try:
        # Find the most recently active device for this license
        # For PRO/Enterprise, we might have multiple devices. 
        # For simplicity, we return the first active one or sort by last_checkin.
        license_obj = License.objects.get(key=key)
        
        if not license_obj.is_active:
             return JsonResponse({'error': 'License suspended'}, status=403)

        device = license_obj.devices.order_by('-last_checkin').first()
        
        if not device:
             return JsonResponse({'error': 'No devices active on this license'}, status=404)

        return JsonResponse({
            'name': device.name,
            'local_ip': device.local_ip,
            'public_ip': device.public_ip, # If we implement WAN tunnelling later
            'port': device.port,
            'last_seen': device.last_checkin,
            'status': 'online' # Logic to check if last_seen < 5 mins ago
        })

    except License.DoesNotExist:
        return JsonResponse({'error': 'Invalid License Key'}, status=404)

@csrf_exempt
def heartbeat(request):
    """
    Endpoint for Local Server to report its status and IP.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
        
    try:
        key = request.GET.get('key') or request.POST.get('key')
        hwid = request.GET.get('hwid') or request.POST.get('hwid')
        
        # Also accept JSON body
        if not key or not hwid:
            try:
                data = json.loads(request.body)
                key = data.get('key')
                hwid = data.get('hwid')
            except:
                pass

        if not key or not hwid:
            return JsonResponse({'error': 'key and hwid required'}, status=400)

        device = Device.objects.get(license__key=key, hardware_id=hwid)
        
        # Update IP info
        # We can detect public IP from request.META
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            public_ip = x_forwarded_for.split(',')[0]
        else:
            public_ip = request.META.get('REMOTE_ADDR')

        # Local IP should be sent by the device payload
        try:
            data = json.loads(request.body)
            local_ip = data.get('local_ip')
            port = data.get('port', 8000)
            version = data.get('version')
            
            if local_ip:
                device.local_ip = local_ip
            if port:
                device.port = port
            if version:
                device.version = version
        except:
            pass # Just a ping
            
        device.public_ip = public_ip
        device.save() # Updates last_checkin automatically
        
        return JsonResponse({'status': 'ok', 'commands': []})

    except Device.DoesNotExist:
        return JsonResponse({'error': 'Device not found or key mismatch'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def check_activation(request):
    """
    Endpoint for local server to check its license status.
    """
    hwid = request.GET.get('hwid')
    if not hwid:
        return JsonResponse({'error': 'hwid required'}, status=400)
        
    try:
        # Check if any device matches this HWID and has an active license
        device = Device.objects.get(hardware_id=hwid)
        if device.license.is_active:
             return JsonResponse({
                'is_active': True,
                'license_key': device.license.key,
                'tier': device.license.tier
            })
        else:
             return JsonResponse({'is_active': False, 'error': 'License expired or suspended'}, status=403)
             
    except Device.DoesNotExist:
        return JsonResponse({'status': 'unregistered'}, status=404)
