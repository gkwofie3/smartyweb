from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('checkout/',          views.checkout,          name='checkout'),
    path('verify/',            views.verify,             name='verify'),
    path('webhook/paystack/',  views.paystack_webhook,  name='webhook'),
    path('success/',           views.success,            name='success'),
    path('cancel/',            views.cancel,             name='cancel'),
]
