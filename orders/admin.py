from django.contrib import admin
from .models import Order, OrderItem

# 1. This tells Django to display the items INSIDE the main order page
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # This creates a handy search widget for products instead of a massive dropdown menu
    raw_id_fields = ['product'] 

# 2. This customizes the main Order list view for the business owner
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # What columns show up in the main list
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'paid', 'created', 'updated']
    
    # Creates a filter sidebar so they can easily find unpaid or recent orders
    list_filter = ['paid', 'created', 'updated']
    
    # Attaches the items to the bottom of the order details page
    inlines = [OrderItemInline]