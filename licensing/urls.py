from django.urls import path
from . import views

urlpatterns = [
    path('activate/', views.activate_license, name='activate_license'),
]
