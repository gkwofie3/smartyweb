from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
    path('api/licensing/', include('licensing.urls')),   # Machine-to-machine API
    path('licensing/', include('licensing.urls')),       # Legacy browser portal
    path('users/', include('users.urls')),
    path('payment/', include('payment.urls')),           # Paystack checkout & webhooks
]
