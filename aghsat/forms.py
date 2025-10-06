# aghsat/forms.py

from django import forms
from django_jalali.forms import jDateField
from django_jalali.admin.widgets import AdminjDateWidget
from .models import Customer, Installment


class CustomerForm(forms.ModelForm):
    """فرم اطلاعات مشتری"""
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'mobile', 'line_sold']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09121234567',
                'maxlength': '11'
            }),
            'line_sold': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: سیمکارت اعتباری'
            }),
        }
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'mobile': 'شماره موبایل',
            'line_sold': 'خط فروخته شده',
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile.startswith('09') or len(mobile) != 11:
            raise forms.ValidationError('شماره موبایل باید با 09 شروع شود و 11 رقم باشد')
        return mobile


class InstallmentForm(forms.ModelForm):
    """فرم قسط"""
    
    payment_date = jDateField(
        label='تاریخ پرداخت',
        widget=AdminjDateWidget(attrs={
            'class': 'form-control jalali-date',
            'placeholder': '1404/01/01'
        })
    )
    
    class Meta:
        model = Installment
        fields = ['amount', 'payment_date']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مبلغ به تومان'
            }),
        }
        labels = {
            'amount': 'مبلغ قسط (تومان)',
            'payment_date': 'تاریخ پرداخت',
        }
