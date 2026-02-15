from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('pricing/', views.pricing, name='pricing'),
    path('faq/', views.faq, name='faq'),
    path('docs/', views.docs, name='docs'),
    path('contact/', views.contact, name='contact'),
]
