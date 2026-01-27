from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product

def product_list(request):
    layout = request.GET.get('layout', 'grid')
    category = request.GET.get('category')
    material = request.GET.get('material')
    sort_by = request.GET.get('sort', 'name')

    products = Product.objects.all()
    
    # Apply filters
    if category:
        products = products.filter(category=category)
    if material:
        products = products.filter(material=material)

    # Apply sorting
    if sort_by == 'price-low':
        products = products.order_by('price_inr')
    elif sort_by == 'price-high':
        products = products.order_by('-price_inr')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('name')

    # Get unique categories and materials
    categories = Product.objects.values_list('category', flat=True).distinct()
    materials = Product.objects.values_list('material', flat=True).distinct()

    context = {
        'products': products,
        'layout': layout,
        'categories': categories,
        'materials': materials,
        'selected_category': category,
        'selected_material': material,
        'selected_sort': sort_by,
    }
    return render(request, 'products/product_list.html', context)
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product_id)[:3]
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        # No need for user_currency - it's now in request.currency
    })

@login_required
def add_to_cart(request, product_id):
    return redirect('checkout', product_id=product_id)

@login_required
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'orders/checkout.html', {'product': product})
# In any view
def your_view(request):
    current_ip = request.ip_address  # This will be manual or auto-detected
    # Use current_ip for geolocation, pricing, etc.