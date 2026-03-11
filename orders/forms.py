from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        # We only ask for these specific fields; Django handles the 'created' and 'paid' fields automatically in the background
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
        
        # We are adding Bootstrap classes here so the form looks premium and modern instantly
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Delivery Street'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nairobi'}),
        }