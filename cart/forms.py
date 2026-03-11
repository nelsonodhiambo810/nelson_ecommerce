from django import forms

# Create a list of numbers from 1 to 20 for the dropdown menu
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int
    )
    # This hidden field tells the cart whether to add to the existing quantity or override it
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )