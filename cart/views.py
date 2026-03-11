import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from store.models import Product
from .cart import Cart
from .forms import CartAddProductForm  # <-- Import the form we built!

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    # Grab the product using the ID from the URL
    product = get_object_or_404(Product, id=product_id)
    
    # Catch the data from the dropdown menu form
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        # Add the item to the cart, multiplying by the quantity they selected!
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
                 
    # Instantly teleport them to your Cart Summary page
    return redirect('cart:cart_summary')

def cart_summary(request):
    return render(request, 'cart/cart_summary.html')

def cart_delete(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id')) # Ensure it's a string if your cart keys are strings
        
        cart.delete(product=product_id)
        
        cart_quantity = len(cart)
        cart_total = cart.get_total_price()
        
        return JsonResponse({'qty': cart_quantity, 'total': cart_total})

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_summary')