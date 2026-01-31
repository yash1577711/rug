from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('create-order/', views.create_order_view, name='create_order'),
    path('success/', views.order_success, name='order_success'),
    path('cancel/', views.order_cancel, name='order_cancel'),
    path('user-orders/', views.user_orders, name='user_orders'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('razorpay-webhook/', views.razorpay_webhook, name='razorpay_webhook'),
]
