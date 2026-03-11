from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomRegistrationForm # <-- Import our new custom form!

def register(request):
    if request.method == 'POST':
        # Use the custom form instead of UserCreationForm
        form = CustomRegistrationForm(request.POST)
        
        if form.is_valid():
            form.save() 
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('accounts:login')
            
    else:
        # Use the custom form for the blank page too
        form = CustomRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})