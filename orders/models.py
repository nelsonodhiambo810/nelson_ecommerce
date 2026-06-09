"""
orders/models.py — Updated with M-Pesa callback fields.

New fields added:
  - mpesa_checkout_request_id: Links the STK Push to this order
  - mpesa_receipt_number: Stored when Safaricom confirms payment

Run migrations after replacing this file:
  python manage.py makemigrations orders
  python manage.py migrate
"""

from django.db import models
from django.contrib.auth.models import User
from store.models import Product


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders'
    )

    # ─── Customer Details ─────────────────────────────────────
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    # ─── Shipping Details ─────────────────────────────────────
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)

    # ─── Payment Status ───────────────────────────────────────
    paid = models.BooleanField(default=False)

    # ─── M-Pesa Fields (NEW) ──────────────────────────────────
    # Stored when STK Push is triggered — used to match the callback
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, default='')
    # Stored when Safaricom confirms payment via callback
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, default='')

    # ─── Timestamps ───────────────────────────────────────────
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['mpesa_checkout_request_id']),  # Fast callback lookup
            models.Index(fields=['paid']),                        # Fast paid/unpaid queries
        ]

    def __str__(self):
        return f'Order {self.id} — {"PAID" if self.paid else "PENDING"}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name='order_items', on_delete=models.SET_NULL, null=True
    )
    # Snapshot price at time of purchase — not linked live to Product.price
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'OrderItem {self.id} (Order #{self.order.id})'

    def get_cost(self):
        return self.price * self.quantity
