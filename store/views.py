from django.shortcuts import render, get_object_or_404
from django.db.models import Q  # <-- Add this new import for the Search function!
from .models import Product, Category
from cart.forms import CartAddProductForm

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()

    # 1. THE SEARCH LOGIC
    # Catch the word the user typed into the search bar
    query = request.GET.get('q')
    if query:
        # Search for the word in the product's name OR description
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # 2. THE CATEGORY LOGIC
    # If they clicked a specific category button, filter the products
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query, # Pass the search word back to the HTML
    })

# ... (Keep your product_detail view exactly as it is) ...

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    # 1. We create the form
    cart_product_form = CartAddProductForm() 
    
    # 2. THE FIX: We pack the form into the curly braces so the HTML can see it!
    return render(request, 'store/product_detail.html', {
        'product': product,
        'cart_product_form': cart_product_form  # <-- Make sure this line is here!
    })