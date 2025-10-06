# aghsat/management/commands/test_sms.py

import os
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SogandAghsat.settings')
django.setup()

from django.core.management.base import BaseCommand
from aghsat.sms_service import send_tomorrow_reminders


class Command(BaseCommand):
    help = 'تست ارسال یادآوری‌های فردا'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('شروع تست ارسال یادآوری‌ها...'))
        
        result = send_tomorrow_reminders()
        
        if result:
            self.stdout.write(self.style.SUCCESS(
                f"✅ ارسال با موفقیت انجام شد:\n"
                f"   - موفق: {result['success']}\n"
                f"   - ناموفق: {result['failed']}\n"
                f"   - کل: {result['total']}"
            ))
        else:
            self.stdout.write(self.style.ERROR('❌ خطا در ارسال یادآوری‌ها'))
