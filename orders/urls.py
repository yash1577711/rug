# orders/urls.py
from django.urls import path
from . import views


    # For now, keep it minimal to avoid errors
    # orders/urls.py
urlpatterns = [
    # ... existing URLs
    path('create-order/', views.create_order_view, name='create_order'),
        path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhook/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
]
