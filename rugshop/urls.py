# rugshop/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from core.views import CustomPasswordResetConfirmView

from core import views as core_views 
from orders import views as orders_views
from orders import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('emergency-admin/', core_views.emergency_admin_login, name='emergency_admin'),
    path('create-admin/', core_views.create_admin_user, name='create_admin'),
    path('', core_views.home, name='home'),
    path('products/', include('products.urls')),  
    path('orders/', include('orders.urls')),
    path('trade/', core_views.trade_view, name='trade'),
    path('owner/', core_views.owner_dashboard, name='owner_dashboard'),
    path('robots.txt', core_views.robots_txt),
    path('accounts/password/reset/key/<uidb64>/<token>/', 
         CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('accounts/', include('allauth.urls')),
    path('about/', core_views.about, name='about'),
    path('set-ip/', core_views.set_manual_ip, name='set_manual_ip'),
    path('set-currency/', core_views.set_currency, name='set_currency'),
    path('api/currency-info/', core_views.get_currency_info, name='currency_info'),
    path('my-orders/', views.user_orders, name='user_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    
]

