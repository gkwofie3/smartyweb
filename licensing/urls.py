from django.urls import path
from . import views

urlpatterns = [
    # Pre-install key check (no auth, called by installer)
    path('check-key/',   views.check_key,   name='license_check_key'),
    # Activate a device (called by smarty.exe --activate)
    path('activate/',    views.activate,    name='license_activate'),
    # Heartbeat / re-validate (called every 6 h by running smarty)
    path('validate/',    views.validate,    name='license_validate'),
    # Deactivate / revoke a device
    path('deactivate/',  views.deactivate,  name='license_deactivate'),
    # Status query (admin / debugging)
    path('status/',      views.status,      name='license_status'),

    # Legacy activate page (keep for backward compat)
    path('activate-device/', views.activate_device_page, name='activate_device'),
]
