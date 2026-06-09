"""
cart/cart.py — Production hardened.

Changes:
  1. __iter__ now uses select_related('category') — no extra query per product
  2. Removed duplicate delete() method — remove() does the same thing
  3. Added __contains__ helper — lets templates do {% if product in cart %}
  4. get_total_price uses cached Decimal values from __iter__ context,
     but the standalone method is kept safe with its own Decimal cast
"""

from decimal import Decimal
from store.models import Product


class Cart:
    SESSION_KEY = 'cart'

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if cart is None:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        # select_related avoids a category query per product
        products = (
            Product.objects
            .filter(id__in=product_ids)
            .select_related('category')
        )
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def __contains__(self, product):
        """Allows: {% if product in cart %} in templates."""
        return str(product.id) in self.cart

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        del self.session[self.SESSION_KEY]
        self.session.modified = True
