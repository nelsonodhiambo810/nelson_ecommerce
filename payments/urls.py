from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process'),
    path('pending/<int:order_id>/', views.payment_pending, name='pending'),
    path('status/<int:order_id>/', views.payment_status, name='status'),
    path('callback/', views.mpesa_callback, name='callback'),
    path('completed/<int:order_id>/', views.payment_completed, name='completed'),
]