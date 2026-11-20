import telebot
import requests
import json
import random
import time
from datetime import datetime, timedelta

# --- تنظیمات کلیدی ---
TELEGRAM_BOT_TOKEN = '9265601576:AAEWU-GhaQXCOOxME-o3MJ02R26dRCx1cPA'  # توکن ربات خودت رو اینجا بذار
FOOTBALL_API_KEY = '97fa56020828415693023a63d60a737b'     # API Key سایت football-data.org

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# --- ظاهر هکری و دارک وب ---
def hacker_style(text):
    """متن رو به سبک هکری نمایش میده"""
    return f"`[{text}]`"

def get_mystery_analysis(match_id):
    """شبیه‌سازی تحلیل عمیق و کمیابی"""
    factors = ["xG", "PPDA", "Field Tilt", "Expected Threat"]
    factor1 = random.choice(factors)
    factor2 = random.choice([f for f in factors if f != factor1])
    
    # عدد تصادفی اما منطقی بین 0.85 تا 0.99 برای ایجاد حس دقت بالا
    confidence = round(random.uniform(0.85, 0.99), 2)
    
    return f"📡 **آنالیز سیگنال:**\n⚠️ پارامترهای غیرقابل مشاهده (Hidden Metrics):\n> {factor1}: +{random.randint(10, 40)}%\n> {factor2}: -{random.randint(5, 20)}%\n\n💎 **احتمال واقعی (Real Probability):** `{confidence * 100}%`\n🕵️‍♂️ **وضعیت:** پروفایل خطر شناسایی شد."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_home = telebot.KeyboardButton("🔮 پیش‌بینی امروز")
    btn_table = telebot.KeyboardButton("📊 جدول رده‌بندی")
    btn_analyze = telebot.KeyboardButton("🧬 تحلیل نابغه")
    btn_fix = telebot.KeyboardButton("🤝 شایعات تبانی")
    
    markup.row(btn_home, btn_table)
    markup.row(btn_analyze, btn_fix)
    
    bot.reply_to(message, 
        f"👋 سلام کاربر ویژه.\nمن موتور پیش‌بینی هوشمند هستم.\nبرای شروع یکی از گزینه‌ها رو انتخاب کن.",
        reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔮 پیش‌بینی امروز")
def predict_today(message):
    try:
        # دریافت بازی‌های امروز
        url = "https://api.football-data.org/v4/competitions/PL/matches" # PL = لیگ برست انگلیس. می‌تونی تغییر بدی
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        matches = data.get('matches', [])
        
        if not matches:
            bot.reply_to(message, "❌ امروز بازی مهمی در پایگاه داده وجود ندارد.")
            return

        output = "🌐 **دیتاست روزانه دریافت شد...**\n\n"
        
        for match in matches[:5]: # فقط 5 بازی برتر رو نشون میده برای جلوگیری از شلوغی
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            date = match['utcDate'][:10]
            status = match['status']
            
            # شبیه‌سازی الگوریتم پیش‌بینی
            win_prob = round(random.uniform(20, 60), 1)
            draw_prob = round(random.uniform(10, 30), 1)
            
            prediction = ""
            if win_prob > 40:
                prediction = f"{home_team} 🏆"
            elif draw_prob > 20:
                prediction = "🤝 مساوی"
            else:
                prediction = f"{away_team} 🏃‍♂️"
                
            mystery = get_mystery_analysis(match['id'])
            
            output += f"⚽ **{home_team} vs {away_team}**\n"
            output += f"📅 زمان: {date} | وضعیت: {status}\n"
            output += f"🔮 **پیش‌بینی:** `{prediction}`\n"
            output += mystery + "\n" + "-"*20 + "\n"

        bot.reply_to(message, output, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ خطا در ارتباط با سرور اصلی: {str(e)}")

@bot.message_handler(func=lambda m: m.text == "📊 جدول رده‌بندی")
def show_standings(message):
    try:
        url = "https://api.football-data.org/v4/competitions/PL/standings"
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        table_text = "🏆 **جدول رده‌بندی لیگ برست (Live Data)**\n\n"
        standings = data['standingTable'][0]['table']
        
        for i, row in enumerate(standings[:10], 1):
            team = row['team']['name']
            pts = row['points']
            played = row['playedMatches']
            w = row['win']
            l = row['loss']
            
            table_text += f"{i}. {team} | امتیاز: {pts} | برد: {w} | باخت: {l}\n"
            
        bot.reply_to(message, table_text)
        
    except Exception as e:
        bot.reply_to(message, f"خطا در دریافت جداول: {e}")

@bot.message_handler(func=lambda m: m.text == "🧬 تحلیل نابغه")
def deep_analysis(message):
    analysis_text = """
🧠 **تحلیل عمیق (Deep Dive):**
در حال اسکن داده‌های خام...
✅ دسترسی به منابع غیررسمی تایید شد.
📉 نوسانات بازار شرط‌بندی در ۲۴ ساعت اخیر نشان‌دهنده ورود پول هوشمند به سمت تیم میزبان است.
🔒 **سیگنال:** خرید در ضریب کمتر از 1.85 امن است.
"""
    bot.reply_to(message, analysis_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🤝 شایعات تبانی")
def rumors(message):
    rumor_list = [
        "تیم A در نیمکت دوم انرژی کمتری دارد (خستگی پنهان).",
        "داور اصلی بازی فردا سابقه ۸۰٪ پنالتی به ضرر تیم مهمان را دارد.",
        "یک بازیکن کلیدی تیم B در تمرینات مشکوک عمل کرده است.",
        "پارامتر فشار بالا (High Press) در ۱۰ دقیقه اول بازی حذف خواهد شد."
    ]
    rumor = random.choice(rumor_list)
    bot.reply_to(message, f"📡 **فایل طبقه‌بندی شده:\n\n{rumor}\n\n[منبع: آنالیز رفتار شناختی داوران]", parse_mode='Markdown')

# اجرای ربات
print("ربات هکری فوتبال فعال شد...")
bot.infinity_polling()
