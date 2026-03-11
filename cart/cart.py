from decimal import Decimal
from store.models import Product

class Cart():
    def __init__(self, request):
        self.session = request.session
        
        # Check if the user already has a cart session going
        cart = self.session.get('session_key')
        
        # If they are a new user, create an empty dictionary for their cart
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
            
        # Make the cart available to all methods in this class
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        # The session cart needs the ID to be a string
        product_id = str(product.id)
        
        # If the gear isn't in the cart yet, add it with a base quantity of 0
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
            
        # If the user selected a new number from the dropdown, override or add it!
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
        # Save the cart
        self.save()

    def save(self):
        """
        Tells Django that the cart has been changed so it saves the session.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart completely.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            
    def __iter__(self):
        # 1. Get all the product IDs currently in the cart dictionary
        product_ids = self.cart.keys()
        
        # 2. Fetch those exact products from the database
        products = Product.objects.filter(id__in=product_ids)
        
        # 3. Make a copy of the cart so we don't accidentally modify the live session
        cart = self.cart.copy()
        
        # 4. Add the actual database product object to our cart dictionary
        for product in products:
            cart[str(product.id)]['product'] = product
            
        # 5. THE FIX: Calculate the math for each item!
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']  # <-- The missing subtotal math!
            yield item

    def __len__(self):
        # THE FIX: Count the total quantity of items, not just the number of unique products
        return sum(item['quantity'] for item in self.cart.values())

    def delete(self, product_id):
        # Convert the ID to a string to match our dictionary keys
        product_id = str(product_id)
        
        # If the product exists in the cart, delete it
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        # THE FIX: Multiply the price by the quantity for the grand total!
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Remove cart from session
        del self.session['session_key']
        self.session.modified = True