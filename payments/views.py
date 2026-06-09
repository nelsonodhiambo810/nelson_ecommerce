"""
payments/views.py — Production-grade M-Pesa integration.

KEY FIX: The original code redirected to 'completed' immediately after the
STK Push was *sent*, not after the customer actually *paid*. This meant
order.paid was never set to True.

The correct flow is:
  1. User submits phone number → trigger STK Push → show "pending" page
  2. Customer enters M-Pesa PIN on their phone
  3. Safaricom calls our /payments/callback/ endpoint (server-to-server)
  4. Callback handler verifies the payment and marks order.paid = True
  5. User is shown a status page they can poll or refresh
"""

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from orders.models import Order
from .utils import trigger_stk_push

logger = logging.getLogger('payments')


def process_payment(request, order_id):
    """
    Step 1: Show payment form and trigger the STK Push.
    After triggering, redirect to a 'pending' page — NOT completed.
    """
    order = get_object_or_404(Order, id=order_id)

    # If already paid, skip straight to completed
    if order.paid:
        return redirect('payments:completed', order_id=order.id)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()

        # Normalize phone: 07xx → 2547xx
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        # Handle +254 format
        elif phone_number.startswith('+254'):
            phone_number = phone_number[1:]

        # Basic validation
        if not phone_number.startswith('254') or len(phone_number) != 12:
            messages.error(request, 'Please enter a valid Safaricom number (e.g. 0712345678)')
            return render(request, 'payments/process.html', {'order': order})

        # Use actual order total, not hardcoded 1
        amount = int(order.get_total_cost())

        logger.info(f'Triggering STK Push for Order #{order.id} — KES {amount} to {phone_number}')

        response = trigger_stk_push(phone_number, amount, order.id)

        if response.get('ResponseCode') == '0':
            # Store the CheckoutRequestID so we can match the callback later
            order.mpesa_checkout_request_id = response.get('CheckoutRequestID', '')
            order.save(update_fields=['mpesa_checkout_request_id'])

            logger.info(f'STK Push sent for Order #{order.id}. CheckoutRequestID: {order.mpesa_checkout_request_id}')

            # Redirect to PENDING page — payment not confirmed yet
            messages.success(request, 'M-Pesa prompt sent! Enter your PIN on your phone.')
            return redirect('payments:pending', order_id=order.id)
        else:
            error_msg = response.get('errorMessage') or response.get('ResponseDescription', 'Unknown error')
            logger.warning(f'STK Push failed for Order #{order.id}: {error_msg}')
            messages.error(request, f'Payment initiation failed: {error_msg}. Please try again.')

    return render(request, 'payments/process.html', {'order': order})


def payment_pending(request, order_id):
    """
    Step 2: Shown after STK Push is sent.
    The customer must complete payment on their phone.
    Page auto-refreshes to check status.
    """
    order = get_object_or_404(Order, id=order_id)

    # If callback already came through, forward to completed
    if order.paid:
        return redirect('payments:completed', order_id=order.id)

    return render(request, 'payments/pending.html', {'order': order})


def payment_status(request, order_id):
    """
    AJAX endpoint: frontend polls this to check if order.paid flipped to True.
    Called every few seconds from the pending page.
    """
    order = get_object_or_404(Order, id=order_id)
    return JsonResponse({
        'paid': order.paid,
        'redirect_url': f'/payments/completed/{order.id}/' if order.paid else None,
    })


@csrf_exempt   # Safaricom's servers POST here — no CSRF token
@require_POST
def mpesa_callback(request):
    """
    Step 3: Safaricom calls this endpoint after the customer pays (or cancels).
    This is server-to-server — the customer never sees this URL.

    IMPORTANT: Always return HTTP 200 to Safaricom, even on errors.
    If you return anything else, Safaricom will retry repeatedly.
    """
    try:
        payload = json.loads(request.body)
        logger.info(f'M-Pesa callback received: {json.dumps(payload, indent=2)}')

        stk_callback = payload['Body']['stkCallback']
        result_code = stk_callback['ResultCode']
        checkout_request_id = stk_callback['CheckoutRequestID']

        # Find the order by the CheckoutRequestID we stored in process_payment
        try:
            order = Order.objects.get(mpesa_checkout_request_id=checkout_request_id)
        except Order.DoesNotExist:
            logger.error(f'Callback received for unknown CheckoutRequestID: {checkout_request_id}')
            return HttpResponse(status=200)

        if result_code == 0:
            # Payment SUCCESS
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            mpesa_receipt = next(
                (item['Value'] for item in callback_metadata if item['Name'] == 'MpesaReceiptNumber'),
                ''
            )

            order.paid = True
            order.mpesa_receipt_number = mpesa_receipt
            order.save(update_fields=['paid', 'mpesa_receipt_number'])
            logger.info(f'Order #{order.id} PAID. M-Pesa receipt: {mpesa_receipt}')

        else:
            # Payment FAILED or CANCELLED by user
            result_desc = stk_callback.get('ResultDesc', 'Payment was not completed')
            logger.warning(f'Order #{order.id} payment failed. Code: {result_code} — {result_desc}')
            # Order remains unpaid — customer can retry

    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f'M-Pesa callback parse error: {e}')

    # Always return 200 to Safaricom
    return HttpResponse(status=200)


def payment_completed(request, order_id):
    """
    Step 4: Final confirmation page — only meaningful if order.paid is True.
    """
    order = get_object_or_404(Order, id=order_id)

    if not order.paid:
        # Edge case: someone navigates here directly before paying
        messages.warning(request, 'Payment not yet confirmed. Please wait for the M-Pesa prompt.')
        return redirect('payments:pending', order_id=order.id)

    return render(request, 'payments/completed.html', {'order': order})
