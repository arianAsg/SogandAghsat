# test_sms_api.py

import requests

class SMSAPITester:
    def __init__(self):
        self.base_url = 'https://skyariacp.com/webservice/url/send.php'
        self.username = 'aria100907'
        self.password = '9197608060'
        self.api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiZThjZGFlNzZiMThmMjJkYTA3NDk3NDA2NzY1OGMxMmVlNzUwMWQyNzBmNzUyY2QzNWY4MDhmNTFmNDMyZmYzNGY1MTQ4YTljMTA1NjkzZTIiLCJpYXQiOjE3NTk3NTAyOTkuODE4ODcyLCJuYmYiOjE3NTk3NTAyOTkuODE4ODcyLCJleHAiOjE3OTEyODYyOTkuODE4ODcyLCJzdWIiOiIxNzkxNSIsInNjb3BlcyI6IltdIn0.KpBphiA4urDEeiesPRnAUiYQAPT-G8xicIcpLKTLNHsdqAnP65WErFN-SNObNL9_jbUe1_y3IxLm2WJ6KJ4wAjL7D8qDGSWWjqal8OR6a8xuvUWrsri--Chx__YlP4Ukn1MohB8La2bb0dmY17Fbqq5XkW6crOMGQ22pEOuZD3wz6kR9pagk48NFuWy5o-gvlZBxLLulf1y9pUbqEvSlSolu-2VE8Iwqqa9GgDFaWAdsMlbXrZVMz3LxgZ7MCVCl10P5eEHC0pSMC7wAqwLbYZrbdF6HtJDy_x_9_jshayExdOyRnBTn0QJ_9YhBtXYYBp6T2GYLrzyU0ivsiw82Hv086r4YYt_qirXX4IC586v0V3Waw0LZzF6sIuA-f1ysW1A3SIXK2kMty8A3Xjv8ieYlQmycXEs_Di5el244wzjTvC_tlSO2qmzOwvLv3UqSjXvaylFS80qifgQg6mof5yPcVJyiEAoE5rieS-w3jirxWQXx6D99VIge6RwJH0FMwZJcTZrmZJyqVX3Z2v5p95yrGsmrg5JuK04dyKLmznoDhXLFUsW1AK-1YQ5knTOzKIJyrIGEEYX1Xfl5qxZN69kNXGWTMkM6H0JoYwK9MD7CO4K3H8ObmtLQdqZV7JVBUGlgbfwwdFnuPkyKtfmW8AsCu9t6Fq_o6VDrr0-sk2Y'
    
    def test_credit(self):
        """تست دریافت اعتبار"""
        print("=" * 60)
        print("تست 1: بررسی اعتبار حساب")
        print("=" * 60)
        
        params = {
            'method': 'getcredit',
            'format': 'json',
            'username': self.username,
            'password': self.password,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    credit = float(data)
                    print(f"\nاعتبار باقیمانده: {credit:,.0f} ریال")
                    
                    if credit <= 0:
                        print("\n⚠️  اعتبار شما صفر است! لطفاً حساب را شارژ کنید.")
                        return False
                    else:
                        print("\n✅ اعتبار کافی است.")
                        return True
                except:
                    print(f"\nکد خطا: {data}")
                    self._explain_error(data)
                    return False
            
        except Exception as e:
            print(f"\n❌ خطا: {str(e)}")
            return False
        
        print("=" * 60)
        return False
    
    def test_send_sms(self, to_number='09121234567', message='تست ارسال پیامک'):
        """تست ارسال پیامک"""
        print("\n" + "=" * 60)
        print("تست 2: ارسال پیامک آزمایشی")
        print("=" * 60)
        print(f"گیرنده: {to_number}")
        print(f"پیام: {message}")
        
        params = {
            'method': 'sendsms',
            'format': 'json',
            'username': self.username,
            'password': self.password,
            'api_key': self.api_key,
            'from': '10001234',  # ⚠️ شماره فرستنده خود را وارد کنید
            'to': to_number,
            'text': message,
            'type': '0'  # 0=عادی، 1=فلش
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                
                if isinstance(result, str) and len(result) == 18:
                    print(f"\n✅ پیامک با موفقیت ارسال شد!")
                    print(f"کد پیگیری: {result}")
                    return True
                else:
                    print(f"\n❌ خطا در ارسال:")
                    self._explain_error(result)
                    return False
            
        except Exception as e:
            print(f"\n❌ خطا: {str(e)}")
            return False
        
        print("=" * 60)
        return False
    
    def _explain_error(self, code):
        """توضیح کدهای خطا"""
        errors = {
            '0': "نام کاربری یا رمز عبور نادرست",
            '1': "اعتبار کافی نیست",
            '2': "شماره فرستنده نامعتبر است",
            '4': "امکان ارسال غیرفعال است",
            '5': "پنل کاربری غیرفعال است",
            '6': "پنل کاربری منقضی شده است",
            '7': "متن پیام خالی است",
            '9': "هیچ گیرنده‌ای وارد نشده",
            '10': "محدودیت زمانی ارسال از خطوط عمومی",
            '11': "خطای نامشخص - با پشتیبانی تماس بگیرید",
        }
        
        code_str = str(code)
        if code_str in errors:
            print(f"کد {code}: {errors[code_str]}")
        else:
            print(f"خطای ناشناخته: {code}")
    
    def run_all_tests(self):
        """اجرای تمام تست‌ها"""
        print("\n🚀 شروع تست‌های API پیامک")
        print("=" * 60)
        
        # تست 1: اعتبار
        if not self.test_credit():
            print("\n⚠️  تست اعتبار موفق نبود. ادامه تست‌ها متوقف شد.")
            return
        
        # تست 2: ارسال (فقط اگر شماره موبایل معتبر وارد کنید)
        print("\n⚠️  برای تست ارسال، شماره موبایل معتبر وارد کنید:")
        print("   (Enter برای رد کردن)")
        phone = input("شماره موبایل (مثال: 09121234567): ").strip()
        
        if phone and phone.startswith('09') and len(phone) == 11:
            self.test_send_sms(to_number=phone)
        else:
            print("\n⏭️  تست ارسال رد شد.")
        
        print("\n✅ تست‌ها به پایان رسید.")
        print("=" * 60)


if __name__ == '__main__':
    tester = SMSAPITester()
    tester.run_all_tests()
