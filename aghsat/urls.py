# aghsat/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_installment, name='create_installment'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('installment/<int:pk>/edit/', views.edit_installment, name='edit_installment'),
    path('installment/<int:pk>/delete/', views.delete_installment, name='delete_installment'),
    path('installment/<int:pk>/toggle/', views.toggle_payment_status, name='toggle_payment_status'),
    path('test-reminders/', views.test_send_reminders, name='test_reminders'),
]
