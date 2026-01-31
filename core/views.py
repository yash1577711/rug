from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum 
from orders.models import Order   
import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

def emergency_admin_login(request):
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'your-email@gmail.com',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    if created:
        admin_user.set_password('EmergencyPass123!')
        admin_user.save()
    
    # Force login
    login(request, admin_user)
    return HttpResponseRedirect(reverse('admin:index'))
def home(request):
    # Get featured products (latest 8)
    featured_products = Product.objects.all().order_by('-created_at')[:8]
    
    return render(request, 'core/home.html', {
        'featured_products': featured_products,
        
    })

def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Allow: /",
        "Sitemap: https://yourdomain.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

# views.py (in core/)
@login_required
def owner_dashboard(request):
    if not request.user.is_superuser:
        return redirect('/')
    
    total_revenue = Order.objects.filter(status='Paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    pending_orders = Order.objects.filter(status='Pending').count()
    shipped_orders = Order.objects.filter(status='Shipped').count()

    context = {
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'shipped_orders': shipped_orders,
        'recent_orders': Order.objects.select_related('user', 'product').order_by('-created_at')[:5]
    }
    return render(request, 'core/owner_dashboard.html', context)
# core/views.py
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

GOOGLE_SHEET_WEBHOOK = "https://script.google.com/macros/s/YOUR_WEBHOOK_URL/exec"

def trade_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        company = request.POST.get('company')
        message = request.POST.get('message')

        payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "message": message
        }

        try:
            response = requests.post(GOOGLE_SHEET_WEBHOOK, json=payload)
            if response.status_code == 200:
                messages.success(request, "Thank you! We’ll contact you soon.")
            else:
                messages.error(request, "Failed to submit. Please try again.")
        except Exception as e:
            messages.error(request, "Network error. Try again later.")

        return redirect('trade')

    return render(request, 'core/trade.html')
# core/views.py
from django.shortcuts import render
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse_lazy

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account_reset_password_complete')
    def form_valid(self, form):
        # Optional: Add any custom logic here
        return super().form_valid(form)
    

from products.models import Product
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from products.models import Product

def about(request):
    # Get some featured products for context
    featured_products = Product.objects.all()[:3]
    return render(request, 'core/about.html', {
        'featured_products': featured_products,
        'user_currency': request.session.get('currency', 'INR')
    })
from django.shortcuts import render, redirect
from django.http import JsonResponse
from ipware import get_client_ip

def set_manual_ip(request):
    if request.method == 'POST':
        manual_ip = request.POST.get('manual_ip')
        if manual_ip:
            request.session['manual_ip'] = manual_ip
        else:
            # Clear manual IP to use auto-detection
            if 'manual_ip' in request.session:
                del request.session['manual_ip']
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('/')


from django.shortcuts import redirect
from django.http import JsonResponse

def set_currency(request):
    if request.method == 'POST':
        currency = request.POST.get('currency')
        if currency in ['INR', 'USD']:
            request.session['manual_currency'] = currency
        else:
            # Clear manual selection to use auto-detection
            if 'manual_currency' in request.session:
                del request.session['manual_currency']
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('/')
# Add this function temporarily
def create_admin_user(request):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'yourpassword123')
    return HttpResponse("Admin user created!")
def get_currency_info(request):
    """API to get current currency info"""
    return JsonResponse({
        'detected_currency': request.session.get('detected_currency', 'INR'),
        'manual_currency': request.session.get('manual_currency', None),
        'current_currency': request.currency,
        'is_manual': 'manual_currency' in request.session
    })
