# orders/admin.py
from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'user', 
        'product', 
        'total_amount', 
        'currency',
        'status', 
        'created_at',
        'payment_id'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['user__email', 'user__username', 'product__name', 'payment_id']
    list_per_page = 20
    
    # Make status editable from list view
    list_editable = ['status']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'product', 'quantity', 'total_amount', 'currency')
        }),
        ('Payment Information', {
            'fields': ('payment_id',)
        }),
        ('Status & Timeline', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )