# aghsat/models.py

from django.db import models
from django_jalali.db import models as jmodels

class Customer(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    mobile = models.CharField(max_length=11, verbose_name='شماره موبایل')
    line_sold = models.CharField(max_length=200, verbose_name='خط فروخته شده')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'مشتری'
        verbose_name_plural = 'مشتریان'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Installment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='installments', verbose_name='مشتری')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='مبلغ قسط')
    payment_date = jmodels.jDateField(verbose_name='تاریخ پرداخت')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    reminder_sent = models.BooleanField(default=False, verbose_name='یادآوری ارسال شده')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = jmodels.jDateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'قسط'
        verbose_name_plural = 'اقساط'
        ordering = ['payment_date']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.payment_date} - {self.amount:,} تومان"
