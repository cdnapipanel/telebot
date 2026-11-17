import asyncio
from pyrogram import Client, filters
from datetime import datetime
import random

# تنظیمات اولیه
# توکن ربات خود را از BotFather دریافت کنید
API_ID = "YOUR_API_ID"  # اگر از اکانت کاربری استفاده می‌کنید، آی‌دی خود را وارد کنید
API_HASH = "YOUR_API_HASH"  # هش خود را وارد کنید
BOT_TOKEN = "YOUR_BOT_TOKEN"  # توکن ربات را اینجا بگذارید

# لیست پسوند یا پیشوند برای تنوع دادن به اسم (اختیاری)
suffixes = ["AI", "🤖", "Bot", "Smart"]

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def update_profile_name():
    """
    تابعی که هر 5 ثانیه نام پروفایل را با ساعت فعلی آپدیت می‌کند
    """
    while True:
        try:
            # دریافت زمان فعلی
            now = datetime.now()
            # فرمت ساعت: HH:MM:SS
            time_str = now.strftime("%H:%M:%S")
            
            # ساخت نام جدید: مثلاً "Name | 14:30:00 AI"
            # می‌توانید نام اصلی خود را جایگزین "MyProfile" کنید یا داینامیک بسازید
            new_name = f"MyProfile | {time_str} 🤖"
            
            # اعمال تغییرات روی پروفایل
            await app.set_username(new_name)
            
            print(f"[{time_str}] Profile name updated to: {new_name}")
            
        except Exception as e:
            print(f"Error updating profile: {e}")
        
        # صبر کردن 5 ثانیه قبل از تغییر بعدی
        await asyncio.sleep(5)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("سلام! من یک هوش مصنوعی هستم که هر 5 ثانیه اسمم رو عوض می‌کنه.")

@app.on_message(filters.command("stop"))
async def stop_command(client, message):
    await message.reply_text("خاموش شدن...")
    # در یک سناریوی واقعی، اینجا می‌توانید حلقه تغییر نام را متوقف کنید

async def main():
    await app.start()
    print("ربات شروع به کار کرد!")
    
    # اجرای همزمان: گوش دادن به پیام‌ها + تغییر مداوم نام پروفایل
    # ما دو تا وظیفه موازی داریم
    
    # 1. گوش دادن به دستورات (start/stop)
    listen_task = asyncio.create_task(app.run())
    
    # 2. تغییر نام پروفایل هر 5 ثانیه
    update_task = asyncio.create_task(update_profile_name())
    
    try:
        await asyncio.gather(listen_task, update_task)
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())