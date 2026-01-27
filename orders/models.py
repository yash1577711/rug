# orders/models.py
from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Generic payment ID (for admin display)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Specific payment IDs
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Webhook verification
    razorpay_webhook_verified = models.BooleanField(default=False)
    stripe_webhook_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.product.name}"
    
    class Meta:
        ordering = ['-created_at']