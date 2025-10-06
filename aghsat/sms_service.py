# aghsat/sms_service.py

import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import Installment

logger = logging.getLogger('aghsat')


class SMSService:
    """سرویس ارسال پیامک با API Sky Aria"""
    
    def __init__(self):
        self.api_url = settings.SMS_CONFIG['API_URL']
        self.username = settings.SMS_CONFIG['USERNAME']
        self.password = settings.SMS_CONFIG['PASSWORD']
        self.api_key = settings.SMS_CONFIG['API_KEY']
        self.from_number = settings.SMS_CONFIG['FROM_NUMBER']
    
    def send_sms(self, to_number, message, is_flash=False):
        """
        ارسال پیامک تکی
        
        Args:
            to_number (str): شماره موبایل گیرنده (مثال: 09121234567)
            message (str): متن پیامک
            is_flash (bool): آیا پیامک فلش باشد؟
            
        Returns:
            dict: نتیجه ارسال شامل success و message_id یا error
        """
        params = {
            'method': 'sendsms',
            'format': 'json',
            'username': self.username,
            'password': self.password,
            'api_key': self.api_key,
            'from': self.from_number,
            'to': to_number,
            'text': message,
            'type': '1' if is_flash else '0'
        }
        
        try:
            logger.info(f"ارسال پیامک به {to_number}")
            response = requests.get(self.api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # بررسی نوع پاسخ
                if isinstance(result, str) and len(result) == 18:
                    # کد 18 رقمی = موفقیت
                    logger.info(f"پیامک با موفقیت ارسال شد. کد پیگیری: {result}")
                    return {'success': True, 'message_id': result}
                elif isinstance(result, (int, str)):
                    # کد خطا
                    error_msg = self._explain_error(result)
                    logger.error(f"خطا در ارسال پیامک به {to_number}: {error_msg}")
                    return {'success': False, 'error': error_msg, 'code': result}
                else:
                    logger.error(f"پاسخ نامعتبر از API: {result}")
                    return {'success': False, 'error': 'پاسخ نامعتبر از سرور'}
            else:
                logger.error(f"خطای HTTP {response.status_code}: {response.text}")
                return {'success': False, 'error': f'خطای HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            logger.error(f"تایم‌اوت در ارسال به {to_number}")
            return {'success': False, 'error': 'زمان انتظار به پایان رسید'}
        except Exception as e:
            logger.error(f"خطای غیرمنتظره در ارسال به {to_number}: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def send_bulk_sms(self, recipients):
        """
        ارسال پیامک گروهی
        
        Args:
            recipients (list): لیست دیکشنری‌های شامل to_number و message
            
        Returns:
            dict: آمار ارسال شامل total, success, failed
        """
        results = {
            'total': len(recipients),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        for recipient in recipients:
            result = self.send_sms(
                to_number=recipient['to_number'],
                message=recipient['message'],
                is_flash=recipient.get('is_flash', False)
            )
            
            if result['success']:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'to_number': recipient['to_number'],
                'result': result
            })
        
        logger.info(f"ارسال گروهی: {results['success']} موفق، {results['failed']} ناموفق")
        return results
    
    def check_credit(self):
        """بررسی اعتبار باقیمانده"""
        params = {
            'method': 'getcredit',
            'format': 'json',
            'username': self.username,
            'password': self.password,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=10)
            if response.status_code == 200:
                credit = response.json()
                if isinstance(credit, (int, float, str)):
                    try:
                        return float(credit)
                    except:
                        return 0.0
            return 0.0
        except Exception as e:
            logger.error(f"خطا در دریافت اعتبار: {str(e)}")
            return 0.0
    
    def _explain_error(self, code):
        """توضیح کدهای خطا بر اساس مستندات"""
        errors = {
            '0': 'نام کاربری یا رمز عبور نادرست',
            '1': 'اعتبار کافی نیست',
            '2': 'شماره فرستنده نامعتبر است',
            '4': 'امکان ارسال غیرفعال است',
            '5': 'پنل کاربری غیرفعال است',
            '6': 'پنل کاربری منقضی شده است',
            '7': 'متن پیام خالی است',
            '9': 'هیچ گیرنده‌ای وارد نشده',
            '10': 'محدودیت زمانی ارسال از خطوط عمومی',
            '11': 'خطای نامشخص - با پشتیبانی تماس بگیرید',
            '16': 'تعداد آرایه بیش از حد مجاز است',
            '22': 'ورودی‌ها به درستی وارد شده',
            '23': 'نوع متغیر method نادرست است',
        }
        
        code_str = str(code)
        return errors.get(code_str, f'خطای ناشناخته: {code}')


def send_tomorrow_reminders():
    """
    ارسال یادآوری برای اقساطی که فردا سررسید دارند
    این تابع توسط scheduler هر روز ساعت 10 صبح اجرا می‌شود
    """
    logger.info("=" * 50)
    logger.info("شروع فرآیند ارسال یادآوری‌های فردا")
    
    # محاسبه تاریخ فردا
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # یافتن اقساط فردا که پرداخت نشده‌اند
    installments = Installment.objects.filter(
        due_date=tomorrow,
        is_paid=False,
        customer__phone__isnull=False
    ).exclude(
        customer__phone=''
    ).select_related('customer')
    
    count = installments.count()
    logger.info(f"تعداد اقساط فردا: {count}")
    
    if count == 0:
        logger.info("هیچ قسطی برای فردا یافت نشد")
        logger.info("=" * 50)
        return {'total': 0, 'success': 0, 'failed': 0}
    
    # آماده‌سازی لیست گیرندگان
    recipients = []
    for installment in installments:
        message = (
            f"سلام {installment.customer.name} عزیز\n"
            f"یادآوری: قسط شما به مبلغ {installment.amount:,} تومان "
            f"فردا ({installment.due_date.strftime('%Y/%m/%d')}) سررسید دارد.\n"
            f"لطفاً نسبت به پرداخت آن اقدام فرمایید."
        )
        
        recipients.append({
            'to_number': installment.customer.phone,
            'message': message,
            'is_flash': False
        })
    
    # ارسال گروهی
    sms_service = SMSService()
    
    # بررسی اعتبار قبل از ارسال
    credit = sms_service.check_credit()
    logger.info(f"اعتبار باقیمانده: {credit:,.0f} ریال")
    
    if credit <= 0:
        logger.error("اعتبار کافی نیست! لطفاً حساب خود را شارژ کنید.")
        return {'total': count, 'success': 0, 'failed': count, 'error': 'اعتبار ناکافی'}
    
    # ارسال
    results = sms_service.send_bulk_sms(recipients)
    
    logger.info(f"نتیجه ارسال: {results['success']} موفق، {results['failed']} ناموفق")
    logger.info("=" * 50)
    
    return results
