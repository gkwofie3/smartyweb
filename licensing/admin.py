from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import License, Device, PricingTier


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display  = ('key', 'user', 'tier', 'components_display', 'max_devices',
                     'device_count', 'is_active', 'expiry_display', 'created_at')
    list_filter   = ('tier', 'is_active')
    search_fields = ('key', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'key')
    ordering      = ('-created_at',)
    actions       = ['suspend_licenses', 'activate_licenses']

    def components_display(self, obj):
        comps = obj.get_components()
        return ', '.join(comps) if comps else '—'
    components_display.short_description = 'Components'

    def device_count(self, obj):
        used  = obj.devices.filter(is_revoked=False).count()
        total = obj.max_devices
        colour = 'red' if used >= total else 'green'
        return format_html('<span style="color:{}">{}/{}</span>', colour, used, total)
    device_count.short_description = 'Devices Used'

    def expiry_display(self, obj):
        if not obj.expiry_date:
            return format_html('<span style="color:green">Lifetime</span>')
        expired = timezone.now() > obj.expiry_date
        colour  = 'red' if expired else 'orange'
        label   = 'EXPIRED' if expired else obj.expiry_date.strftime('%Y-%m-%d')
        return format_html('<span style="color:{}">{}</span>', colour, label)
    expiry_display.short_description = 'Expiry'

    @admin.action(description='Suspend selected licenses')
    def suspend_licenses(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Re-activate selected licenses')
    def activate_licenses(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display  = ('name', 'hardware_id_short', 'license_key', 'tier',
                     'local_ip', 'public_ip', 'version', 'last_checkin',
                     'last_validated', 'is_revoked')
    list_filter   = ('is_revoked', 'license__tier')
    search_fields = ('name', 'hardware_id', 'license__key')
    readonly_fields = ('activated_at', 'last_checkin', 'last_validated')
    actions       = ['revoke_devices', 'restore_devices']

    def hardware_id_short(self, obj):
        return obj.hardware_id[:20] + '…'
    hardware_id_short.short_description = 'HWID'

    def license_key(self, obj):
        return obj.license.key
    license_key.short_description = 'License Key'

    def tier(self, obj):
        return obj.license.tier
    tier.short_description = 'Tier'

    @admin.action(description='Revoke selected devices')
    def revoke_devices(self, request, queryset):
        queryset.update(is_revoked=True)

    @admin.action(description='Restore (un-revoke) selected devices')
    def restore_devices(self, request, queryset):
        queryset.update(is_revoked=False)
