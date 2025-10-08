# aghsat/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, Q, Count
from datetime import timedelta
import jdatetime

from .models import Customer, Installment
from .forms import CustomerForm, InstallmentForm
from .sms_service import send_tomorrow_reminders


def user_login(request):
    """صفحه ورود"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
    
    return render(request, 'aghsat/login.html')


@login_required
def user_logout(request):
    """خروج کاربر"""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """داشبورد اصلی"""
    total_customers = Customer.objects.count()
    total_installments = Installment.objects.count()
    unpaid_installments = Installment.objects.filter(is_paid=False).count()
    
    # اقساط امروز و فردا
    today = jdatetime.date.today()
    tomorrow = today + jdatetime.timedelta(days=1)
    
    today_installments = Installment.objects.filter(
        payment_date=today,
        is_paid=False
    ).count()
    
    tomorrow_installments = Installment.objects.filter(
        payment_date=tomorrow,
        is_paid=False
    ).count()
    
    context = {
        'total_customers': total_customers,
        'total_installments': total_installments,
        'unpaid_installments': unpaid_installments,
        'today_installments': today_installments,
        'tomorrow_installments': tomorrow_installments,
    }
    
    return render(request, 'aghsat/dashboard.html', context)


@login_required
def create_installment(request):
    """ایجاد مشتری و اقساط جدید"""
    if request.method == 'POST':
        customer_form = CustomerForm(request.POST)
        
        if customer_form.is_valid():
            # ذخیره مشتری
            customer = customer_form.save()
            
            # دریافت تعداد اقساط از فرم
            installment_count = int(request.POST.get('installment_count', 0))
            
            if installment_count == 0:
                messages.warning(request, 'حداقل یک قسط را وارد کنید')
                return redirect('create_installment')
            
            # ذخیره اقساط
            saved_count = 0
            for i in range(installment_count):
                amount = request.POST.get(f'amount_{i}')
                payment_date = request.POST.get(f'payment_date_{i}')
                
                if amount and payment_date:
                    try:
                        # تبدیل تاریخ شمسی به میلادی
                        j_date = jdatetime.datetime.strptime(payment_date, '%Y/%m/%d').date()
                        
                        Installment.objects.create(
                            customer=customer,
                            amount=amount,
                            payment_date=j_date
                        )
                        saved_count += 1
                    except Exception as e:
                        messages.error(request, f'خطا در ذخیره قسط {i+1}: {str(e)}')
            
            if saved_count > 0:
                messages.success(request, f'مشتری و {saved_count} قسط با موفقیت ثبت شد')
                return redirect('customer_list')
            else:
                messages.error(request, 'هیچ قسطی ذخیره نشد')
        else:
            messages.error(request, 'لطفا اطلاعات مشتری را به درستی وارد کنید')
    else:
        customer_form = CustomerForm()
    
    context = {
        'customer_form': customer_form,
    }
    
    return render(request, 'aghsat/create_installment.html', context)


@login_required
def customer_list(request):
    """نمایش لیست تمام مشتریان"""
    customers = Customer.objects.all().annotate(
        total_installments=Count('installments'),
        unpaid_installments=Count('installments', filter=Q(installments__is_paid=False))
    ).order_by('-created_at')
    
    context = {
        'customers': customers,
    }
    return render(request, 'aghsat/customer_list.html', context)


@login_required
def customer_detail(request, pk):
    """نمایش جزئیات یک مشتری و اقساط او"""
    customer = get_object_or_404(Customer, pk=pk)
    installments = customer.installments.all().order_by('payment_date')
    
    # محاسبه آمار
    total_amount = installments.aggregate(total=Sum('amount'))['total'] or 0
    paid_amount = installments.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
    remaining_amount = total_amount - paid_amount
    
    # تعداد اقساط پرداخت شده و نشده
    paid_count = installments.filter(is_paid=True).count()
    unpaid_count = installments.filter(is_paid=False).count()
    
    context = {
        'customer': customer,
        'installments': installments,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'remaining_amount': remaining_amount,
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
    }
    return render(request, 'aghsat/customer_detail.html', context)


@login_required
def edit_installment(request, pk):
    """ویرایش قسط"""
    installment = get_object_or_404(Installment, pk=pk)
    
    if request.method == 'POST':
        form = InstallmentForm(request.POST, instance=installment)
        if form.is_valid():
            form.save()
            messages.success(request, 'قسط با موفقیت ویرایش شد')
            return redirect('customer_detail', pk=installment.customer.pk)
    else:
        form = InstallmentForm(instance=installment)
    
    context = {
        'form': form,
        'installment': installment,
    }
    
    return render(request, 'aghsat/edit_installment.html', context)


@login_required
def delete_installment(request, pk):
    """حذف قسط"""
    installment = get_object_or_404(Installment, pk=pk)
    customer_pk = installment.customer.pk
    
    if request.method == 'POST':
        installment.delete()
        messages.success(request, 'قسط با موفقیت حذف شد')
        return redirect('customer_detail', pk=customer_pk)
    
    context = {
        'installment': installment,
    }
    return render(request, 'aghsat/delete_installment.html', context)


@login_required
def toggle_payment_status(request, pk):
    """تغییر وضعیت پرداخت قسط"""
    installment = get_object_or_404(Installment, pk=pk)
    installment.is_paid = not installment.is_paid
    installment.save()
    
    status = 'پرداخت شده' if installment.is_paid else 'پرداخت نشده'
    messages.success(request, f'وضعیت قسط به "{status}" تغییر کرد')
    
    return redirect('customer_detail', pk=installment.customer.pk)


@login_required
def test_send_reminders(request):
    """تست ارسال یادآوری‌ها"""
    if request.method == 'POST':
        result = send_tomorrow_reminders()
        
        if result:
            messages.success(
                request,
                f"یادآوری‌ها با موفقیت ارسال شدند! "
                f"موفق: {result['success']}, ناموفق: {result['failed']}"
            )
        else:
            messages.error(request, "خطا در ارسال یادآوری‌ها!")
        
        return redirect('dashboard')
    
    return redirect('dashboard')
