# aghsat/admin.py

from django.contrib import admin
from .models import Customer, Installment

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'mobile', 'line_sold', 'created_at']
    search_fields = ['first_name', 'last_name', 'mobile']
    list_filter = ['created_at']

@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'amount', 'payment_date', 'is_paid', 'reminder_sent']
    list_filter = ['is_paid', 'reminder_sent', 'payment_date']
    search_fields = ['customer__first_name', 'customer__last_name']
    date_hierarchy = 'payment_date'
