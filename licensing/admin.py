from django.contrib import admin
from .models import License, Device

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'tier', 'max_devices', 'is_active', 'expiry_date')
    list_filter = ('tier', 'is_active')
    search_fields = ('key', 'user__username', 'user__email')
    readonly_fields = ('created_at',)

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'hardware_id', 'license', 'local_ip', 'public_ip', 'last_checkin')
    search_fields = ('name', 'hardware_id', 'license__key')
    readonly_fields = ('activated_at', 'last_checkin')
