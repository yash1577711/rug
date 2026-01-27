from django.contrib import admin
from django.utils.html import format_html
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # List view configuration
    list_display = [
        'name', 
        'price_inr', 
        'price_usd', 
        'category', 
        'material', 
        'created_at',
        'image_thumbnail',
        'is_featured'
    ]
    list_filter = ['category', 'material', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'category', 'material']
    list_per_page = 20
    
    # Form fields configuration
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'image', 'is_featured')
        }),
        ('Pricing', {
            'fields': ('price_inr', 'price_usd')
        }),
        ('Classification', {
            'fields': ('category', 'material')
        }),
        ('SEO', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
    )
    
    # Auto-populate slug from name
    prepopulated_fields = {'slug': ('name',)}
    
    # Custom methods for list display
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return '-'
    image_thumbnail.short_description = 'Image Preview'
    
    # Additional admin options
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    # Bulk actions
    actions = ['make_featured', 'remove_featured', 'export_as_csv']
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products marked as featured.')
    make_featured.short_description = "Mark selected as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} products removed from featured.')
    remove_featured.short_description = "Remove from featured"
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=products.csv'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Price INR', 'Price USD', 'Category', 'Material', 'Created'])
        
        for obj in queryset:
            writer.writerow([obj.name, obj.price_inr, obj.price_usd, obj.category, obj.material, obj.created_at])
        
        return response
    export_as_csv.short_description = "Export selected as CSV"

# If you have other models, register them too
# Example for Order model (if exists):
"""
from orders.models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['created_at']
"""