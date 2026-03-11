from .cart import Cart

# This allows our templates to access the cart dictionary globally
def cart(request):
    return {'cart': Cart(request)}