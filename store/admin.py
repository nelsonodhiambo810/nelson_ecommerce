from django.contrib import admin
from .models import Category, Product

# This automatically generates the slug from the name when you type
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at']
    list_editable = ['price', 'is_available']
    prepopulated_fields = {'slug': ('title',)}