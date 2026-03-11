from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from orders.models import Order
from .utils import trigger_stk_push

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
            
        amount = 1 
        
        response = trigger_stk_push(phone_number, amount, order.id)
        
        if response.get('ResponseCode') == '0':
            # SUCCESS! Redirect them to the completed page
            return redirect('payments:completed', order_id=order.id)
        else:
            messages.error(request, f"Failed to trigger STK Push: {response.get('errorMessage', 'Unknown Error')}")
            
    return render(request, 'payments/process.html', {'order': order})

# Add this new simple view at the bottom:
def payment_completed(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payments/completed.html', {'order': order})