"""
orders/views.py — Production hardened.

Fix:
  quantity=1 was hardcoded in OrderItem.objects.create — a customer who added
  3 units of an item would have their order recorded as quantity 1.
  Now correctly uses item['quantity'] from the cart.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart


def order_create(request):
    cart = Cart(request)

    # Guard: don't let someone submit an empty cart
    if len(cart) == 0:
        return redirect('store:product_list')

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
                    quantity=item['quantity'],  # ← FIX: was hardcoded to 1
                )

            cart.clear()
            return redirect('payments:process', order_id=order.id)

    else:
        # Pre-fill form for logged-in users
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})


@login_required
def user_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related('items__product')  # Avoids N+1 on order item list
        .order_by('-created')
    )
    return render(request, 'orders/order/user_orders.html', {'orders': orders})
