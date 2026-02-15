from django.urls import path
from . import views

urlpatterns = [
    path('resolve/', views.resolve_connection, name='resolve_connection'),
    path('check/', views.check_activation, name='check_activation'),
    path('heartbeat/', views.heartbeat, name='heartbeat'),
]
