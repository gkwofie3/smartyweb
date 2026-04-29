from django.contrib import admin
from django.utils.html import format_html
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('reference', 'email', 'plan', 'usd_display', 'ghs_display',
                      'status_badge', 'created_at', 'license_link')
    list_filter   = ('status', 'plan')
    search_fields = ('reference', 'email', 'paystack_id')
    readonly_fields = ('reference', 'user', 'email', 'plan', 'usd_amount', 'ghs_amount',
                       'ghs_pesewas', 'exchange_rate', 'paystack_id', 'created_at',
                       'paid_at', 'license')
    ordering = ('-created_at',)

    def usd_display(self, obj):
        return f'${obj.usd_amount:,.2f}'
    usd_display.short_description = 'USD Price'

    def ghs_display(self, obj):
        return f'GHS {obj.ghs_amount:,.2f}'
    ghs_display.short_description = 'GHS Charged'

    def status_badge(self, obj):
        colours = {
            'PENDING':  '#f59e0b',
            'PAID':     '#10b981',
            'FAILED':   '#ef4444',
            'REFUNDED': '#6366f1',
        }
        colour = colours.get(obj.status, '#9ca3af')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            colour, obj.status
        )
    status_badge.short_description = 'Status'

    def license_link(self, obj):
        if obj.license:
            return format_html(
                '<a href="/admin/licensing/license/{}/change/">{}</a>',
                obj.license.pk, obj.license.key
            )
        return '—'
    license_link.short_description = 'License'

    def has_add_permission(self, request):
        return False  # Orders are created programmatically only
