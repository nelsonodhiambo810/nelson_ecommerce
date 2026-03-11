from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process'),
    path('completed/<int:order_id>/', views.payment_completed, name='completed'), # <-- Add this!
]