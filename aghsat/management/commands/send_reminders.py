# aghsat/management/commands/send_reminders.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from aghsat.models import Installment
from aghsat.sms_service import send_sms
import jdatetime

class Command(BaseCommand):
    help = 'ارسال یادآوری اقساط فردا'

    def handle(self, *args, **kwargs):
        # تاریخ فردا به شمسی
        tomorrow = jdatetime.date.today() + jdatetime.timedelta(days=1)
        
        # یافتن اقساطی که فردا سررسید دارند و پرداخت نشده‌اند
        installments = Installment.objects.filter(
            payment_date=tomorrow,
            is_paid=False,
            reminder_sent=False
        ).select_related('customer')
        
        sent_count = 0
        failed_count = 0
        
        for installment in installments:
            customer = installment.customer
            message = f"""
سلام {customer.first_name} {customer.last_name} عزیز
یادآوری قسط:
تاریخ: {installment.payment_date}
مبلغ: {installment.amount:,} تومان
خط: {customer.line_sold}
لطفا نسبت به پرداخت اقدام فرمایید.
سوگند سیم
            """.strip()
            
            success, result = send_sms(customer.mobile, message)
            
            if success:
                installment.reminder_sent = True
                installment.save()
                sent_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'پیامک به {customer.get_full_name()} ارسال شد'
                ))
            else:
                failed_count += 1
                self.stdout.write(self.style.ERROR(
                    f'خطا در ارسال پیامک به {customer.get_full_name()}: {result}'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nخلاصه: {sent_count} موفق، {failed_count} ناموفق'
        ))
