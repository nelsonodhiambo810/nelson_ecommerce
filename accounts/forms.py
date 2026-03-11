from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomRegistrationForm(UserCreationForm):
    # We make these required so the auto-fill always works later!
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(required=True, help_text='Required.')

    class Meta:
        model = User
        # This tells Django exactly which fields to show on the sign-up page, and in what order
        fields = ['username', 'first_name', 'last_name', 'email']