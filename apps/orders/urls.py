"""
URLs for the orders app
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('payment/<int:order_id>/', views.initiate_mpesa_payment, name='payment'),
    path('payment/status/<int:order_id>/', views.payment_status, name='payment_status'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
]
