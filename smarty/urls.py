from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
    path('api/', include('api.urls')),
    path('licensing/', include('licensing.urls')),
    path('users/', include('users.urls')),
]
