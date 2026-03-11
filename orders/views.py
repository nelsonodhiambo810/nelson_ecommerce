from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect # <-- 1. Make sure 'redirect' is imported here!
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        
        if form.is_valid():
            order = form.save(commit=False)
            
            if request.user.is_authenticated:
                order.user = request.user
                
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=1 
                )
            
            cart.clear()
            
            # 2. THE MAGIC LINK: Instantly teleport them to the M-Pesa payment page!
            return redirect('payments:process', order_id=order.id)
            
    else:
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
            form = OrderCreateForm(initial=initial_data)
        else:
            form = OrderCreateForm()
        
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})
@login_required
def user_orders(request):
    # Fetch all orders belonging to the logged-in user, sorted by ID (newest first)
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'orders/order/user_orders.html', {'orders': orders})    