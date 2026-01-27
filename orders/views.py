# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Order
from products.models import Product
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    current_currency = getattr(request, 'currency', 'INR')
    
    # Get price based on currency
    if current_currency == 'INR':
        total_amount = product.price_inr
    else:
        total_amount = product.price_usd
    
    context = {
        'product': product,
        'current_currency': current_currency,
        'total_amount': total_amount,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def create_order(request, product_id, payment_id=None):
    """Create order after successful payment"""
    product = get_object_or_404(Product, id=product_id)
    current_currency = getattr(request, 'currency', 'INR')
    
    if current_currency == 'INR':
        total_amount = product.price_inr
    else:
        total_amount = product.price_usd
    
    order = Order.objects.create(
        user=request.user,
        product=product,
        total_amount=total_amount,
        currency=current_currency,
        payment_id=payment_id
    )
    return order

# Update your existing views to create orders
# orders/views.py
@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        try:
            # Create client_reference_id to identify user and product
            client_reference_id = f"{request.user.id}_{product_id}"
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': int(product.price_usd * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                client_reference_id=client_reference_id,  # Critical for webhook
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return redirect('home')
def order_success(request):
    # In real app, verify the session with Stripe
    # For now, create order directly
    # You'll need to pass product_id somehow (via session or URL)
    return render(request, 'orders/success.html')

def order_cancel(request):
    return render(request, 'orders/cancel.html')

# New: User Order Management
@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/user_orders.html', {'orders': orders})

@login_required  
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
# orders/views.py
def create_order_after_payment(user, product_id, payment_id, currency):
    """Create order after successful payment"""
    from products.models import Product
    product = Product.objects.get(id=product_id)
    
    if currency == 'INR':
        total_amount = product.price_inr
    else:
        total_amount = product.price_usd
    
    order = Order.objects.create(
        user=user,
        product=product,
        total_amount=total_amount,
        currency=currency,
        payment_id=payment_id,
        status='confirmed'  # Payment successful, so confirmed
    )
    return order
# orders/views.py
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@login_required
def create_order_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        payment_id = data.get('payment_id')
        currency = data.get('currency')
        
        order = create_order_after_payment(
            request.user, 
            product_id, 
            payment_id, 
            currency
        )
        
        return JsonResponse({'order_id': order.id})
    return JsonResponse({'error': 'Invalid request'})
# orders/views.py
import json
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
import stripe

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
# orders/views.py
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extract user_id and product_id from client_reference_id
        client_reference_id = session.get('client_reference_id')
        if not client_reference_id:
            return HttpResponse(status=400)
            
        try:
            user_id, product_id = client_reference_id.split('_')
            user_id = int(user_id)
            product_id = int(product_id)
            
            # Get the user and product
            from django.contrib.auth.models import User
            from products.models import Product
            
            user = User.objects.get(id=user_id)
            product = Product.objects.get(id=product_id)
            
            # ✅ HERE IS YOUR VERIFICATION LOGIC
            # If your Product model has a 'user' field (seller/owner):
            # if hasattr(product, 'user') and product.user != user:
            #     return HttpResponse(status=400)
            
            # For most e-commerce sites, any user can buy any product
            # So this verification might not be needed unless you have specific business logic
            
            # Create the order
            currency = session['currency'].upper()
            amount = session['amount_total'] / 100
            
            Order.objects.create(
                user=user,
                product=product,
                total_amount=amount,
                currency=currency,
                payment_id=session['payment_intent'],
                stripe_payment_intent_id=session['payment_intent'],
                stripe_webhook_verified=True,
                status='confirmed'
            )
            
        except (ValueError, User.DoesNotExist, Product.DoesNotExist) as e:
            print(f"Webhook error: {e}")
            return HttpResponse(status=400)

    return HttpResponse(status=200)

# orders/views.py
import json
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from products.models import Product
from .models import Order

@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhook events with proper signature verification"""
    
    # Get the webhook secret from settings
    webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
    
    if request.method == 'POST':
        # Get the signature from headers
        signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
        
        if not signature:
            return HttpResponse(status=400)
        
        # Get the payload
        payload = request.body
        
        try:
            # Verify the signature
            if webhook_secret:
                expected_signature = hmac.new(
                    webhook_secret.encode(),
                    payload,
                    hashlib.sha256
                ).hexdigest()
                
                if signature != expected_signature:
                    return HttpResponse(status=400)
            
            # Parse the webhook data
            data = json.loads(payload)
            
            # Handle payment.captured event (most common for successful payments)
            if data.get('event') == 'payment.captured':
                payload_data = data.get('payload', {})
                payment_entity = payload_data.get('payment', {}).get('entity', {})
                
                razorpay_payment_id = payment_entity.get('id')
                razorpay_order_id = payment_entity.get('order_id')
                amount = payment_entity.get('amount', 0) / 100  # Convert from paise to rupees
                currency = payment_entity.get('currency', 'INR')
                
                # Extract notes (you should store user_id and product_id in notes during checkout)
                notes = payment_entity.get('notes', {})
                user_id = notes.get('user_id')
                product_id = notes.get('product_id')
                
                if razorpay_payment_id and user_id and product_id:
                    try:
                        # Get user and product
                        user = User.objects.get(id=int(user_id))
                        product = Product.objects.get(id=int(product_id))
                        
                        # Create order
                        order = Order.objects.create(
                            user=user,
                            product=product,
                            total_amount=amount,
                            currency=currency,
                            payment_id=razorpay_payment_id,
                            razorpay_payment_id=razorpay_payment_id,
                            razorpay_webhook_verified=True,
                            status='confirmed'
                        )
                        
                    except (User.DoesNotExist, Product.DoesNotExist, ValueError) as e:
                        print(f"Error creating order: {e}")
                        return HttpResponse(status=400)
                
            # Handle other events like payment.failed, order.paid, etc.
            elif data.get('event') == 'payment.failed':
                # Handle failed payment
                pass
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Webhook parsing error: {e}")
            return HttpResponse(status=400)
    
    return HttpResponse(status=200)
from django.views.decorators.csrf import csrf_exempt

