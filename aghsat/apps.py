# aghsat/apps.py

from django.apps import AppConfig


class AghsatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aghsat'
    verbose_name = 'مدیریت اقساط'

    def ready(self):
        """فعال‌سازی scheduler هنگام بالا آمدن سرور"""
        import os
        
        # فقط در حالت production و runserver اصلی اجرا شود
        # (نه در migrate یا createsuperuser)
        if os.environ.get('RUN_MAIN') == 'true':
            from .scheduler import start_scheduler
            start_scheduler()
