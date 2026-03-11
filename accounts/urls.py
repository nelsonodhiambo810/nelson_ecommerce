from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Our custom registration page
    path('register/', views.register, name='register'),
    
    # Django's built-in login view (we just tell it which HTML file to use)
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    # Django's built-in logout view (we tell it to redirect to the homepage after logging out)
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]