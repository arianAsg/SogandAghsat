# aghsat/scheduler.py

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
import os

logger = logging.getLogger('aghsat')

def check_and_send_reminders():
    """تابعی که توسط scheduler فراخوانی می‌شود"""
    from .sms_service import send_tomorrow_reminders
    
    logger.info("شروع بررسی اقساط فردا...")
    try:
        result = send_tomorrow_reminders()
        logger.info(f"اتمام بررسی. نتیجه: {result}")
    except Exception as e:
        logger.error(f"خطا در ارسال یادآوری‌ها: {str(e)}", exc_info=True)

# Instance واحد scheduler
scheduler = None

def start_scheduler():
    """راه‌اندازی scheduler برای ارسال خودکار یادآوری‌ها"""
    global scheduler
    
    # فقط در پروسه اصلی Django اجرا شود (جلوگیری از اجرای دوباره)
    if os.environ.get('RUN_MAIN') != 'true':
        return
    
    if scheduler is not None:
        logger.warning("Scheduler قبلاً راه‌اندازی شده است.")
        return
    
    try:
        scheduler = BackgroundScheduler()
        
        # اضافه کردن job برای اجرای روزانه ساعت 10:00 صبح
        scheduler.add_job(
            check_and_send_reminders,
            trigger=CronTrigger(hour=10, minute=0),  # هر روز ساعت 10:00
            id='daily_sms_reminder',
            name='ارسال یادآوری روزانه اقساط',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler با موفقیت راه‌اندازی شد. یادآوری‌ها هر روز ساعت 10:00 ارسال می‌شوند.")
        
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی scheduler: {str(e)}", exc_info=True)

def stop_scheduler():
    """توقف scheduler"""
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler متوقف شد.")
