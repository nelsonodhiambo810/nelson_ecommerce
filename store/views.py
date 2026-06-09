"""
store/views.py — Production hardened.

Fixes:
  1. Added is_available=True filter — unpublished products were showing in search
  2. Added select_related('category') — eliminates N+1 query on product list
  3. Added only() to limit columns fetched from DB on list view
  4. search now strips whitespace and skips empty queries
"""

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    category = None
    # select_related: fetches category in same SQL JOIN — no extra query per product
    categories = Category.objects.all()
    products = (
        Product.objects
        .filter(is_available=True)          # Never show unpublished gear
        .select_related('category')         # 1 query instead of 1 per product
        .only(                              # Fetch only what the list template needs
            'id', 'title', 'slug', 'price',
            'image', 'category__name', 'category__slug'
        )
    )

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
    })


def product_detail(request, slug):
    # is_available=True prevents direct URL access to unlisted products
    product = get_object_or_404(Product, slug=slug, is_available=True)
    cart_product_form = CartAddProductForm()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
    })
