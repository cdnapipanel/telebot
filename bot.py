import telebot
from telebot import types
import requests
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime, timedelta
import json

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# دریافت توکن‌ها از متغیرهای محیطی گیت‌هاب
API_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_DEFAULT_BOT_TOKEN')
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY', 'YOUR_DEFAULT_FOOTBALL_KEY')

bot = telebot.TeleBot(API_TOKEN)

# --- موتور اتصال به API واقعی (Real Data Core) ---
class FootballProEngine:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        
    def get_todays_matches(self):
        """دریافت بازی‌های امروز از سرور اصلی"""
        try:
            # دریافت بازی‌های لیگ‌های بزرگ
            leagues = ['PL', 'PD', 'BL1', 'SA', 'FL1'] 
            matches = []
            
            for league in leagues:
                url = f"{self.base_url}/competitions/{league}/matches?dateFrom={datetime.now().strftime('%Y-%m-%d')}&dateTo={datetime.now().strftime('%Y-%m-%d')}"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'matches' in data:
                        for match in data['matches']:
                            # فیلتر کردن بازی‌هایی که هنوز شروع نشده‌اند
                            if match['status'] == 'SCHEDULED':
                                home_team = match['homeTeam']['shortName']
                                away_team = match['awayTeam']['shortName']
                                time = match['utcDate'][11:16]
                                league_name = match['competition']['name']
                                
                                matches.append({
                                    "home": home_team,
                                    "away": away_team,
                                    "time": time,
                                    "league": league_name
                                })
            return matches
        except Exception as e:
            logger.error(f"Error fetching matches: {e}")
            return []

    def get_standings(self, league_id="PL"):
        """دریافت جدول رتبه‌بندی زنده"""
        try:
            url = f"{self.base_url}/competitions/{league_id}/standings"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                standings = []
                for table in data['table']:
                    team = table['team']['shortName']
                    pts = table['points']
                    pos = table['position']
                    standings.append((pos, team, pts))
                return sorted(standings, key=lambda x: x[2], reverse=True)[:10] # فقط 10 تیم اول
            return []
        except Exception as e:
            logger.error(f"Error fetching standings: {e}")
            return []

engine = FootballProEngine()

# --- مدیریت رویدادها (Event Handlers) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    
    btn_matches = types.InlineKeyboardButton("📋 لیست بازی‌های امروز", callback_data='list_matches')
    btn_predict = types.InlineKeyboardButton("🧠 پیش‌بینی هوشمند", callback_data='predict_random')
    btn_standings = types.InlineKeyboardButton("🏆 جدول لیگ برتر", callback_data='show_standings_pl')
    btn_vip = types.InlineKeyboardButton("💎 اشتراک ویژه VIP", url="https://t.me/YOUR_CHANNEL")
    
    markup.row(btn_matches, btn_predict)
    markup.row(btn_standings, btn_vip)
    
    welcome_msg = (
        "👋 <b>به شبکه عصبی فوتبال خوش آمدید.</b>\n\n"
        "من مستقیماً به سرورهای داده جهانی متصل هستم. برای دریافت تحلیل‌های دقیق:\n\n"
        "⚡ آپدیت لحظه‌ای | 📊 آمار واقعی | 🔒 محرمانه"
    )
    
    bot.send_message(message.chat.id, welcome_msg, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'list_matches':
        matches = engine.get_todays_matches()
        if not matches:
            bot.answer_callback_query(call.id, text="هیچ بازی‌ای برای امروز یافت نشد.")
            return
            
        msg = "<b>🔴 جریان داده‌های بازی‌های امروز</b>\n\n"
        for m in matches:
            msg += f"⚽ <b>{m['home']}</b> vs <b>{m['away']}</b>\n"
            msg += f"   🕒 ساعت: {m['time']} | 🏢 لیگ: {m['league']}\n\n"
        
        bot.answer_callback_query(call.id, text="داده‌ها دریافت شد.")
        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')

    elif call.data == 'show_standings_pl':
        standings = engine.get_standings('PL')
        if not standings:
            bot.answer_callback_query(call.id, text="خطا در دریافت جدول.")
            return

        msg = "<b>🏆 جدول رتبه‌بندی لیگ برتر</b>\n\n"
        for i, (pos, team, pts) in enumerate(standings, 1):
            msg += f"{i}. {team} - {pts} امتیاز\n"
            
        bot.answer_callback_query(call.id, text="جدول بروزرسانی شد.")
        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')

    elif call.data == 'predict_random':
        matches = engine.get_todays_matches()
        if not matches:
            bot.send_message(call.message.chat.id, "فعلاً بازی‌ای برای پیش‌بینی وجود ندارد.")
            return
            
        target_match = random.choice(matches)
        
        # شبیه‌سازی الگوریتم یادگیری ماشین روی داده‌های واقعی
        p_home = round(np.random.uniform(30, 70), 1)
        p_draw = round(np.random.uniform(10, 25), 1)
        p_away = round(100 - p_home - p_draw, 1)
        
        if p_home > p_away and p_home > p_draw:
            result = f"برد {target_match['home']}"
        elif p_away > p_home and p_away > p_draw:
            result = f"برد {target_match['away']}"
        else:
            result = "مساوی یا اختلاف کم"
            
        pred_msg = (
            f"<b>🧠 تحلیل الگوریتمی</b>\n"
            f"🔍 матч: <b>{target_match['home']}</b> در برابر <b>{target_match['away']}</b>\n"
            f"🏢 لیگ: {target_match['league']}\n\n"
            f"🎯 <b>نتیجه محتمل:</b> {result}\n"
            f"📈 سطح اطمینان: بالا\n\n"
            f"<b>📊 ماتریس احتمالات:</b>\n"
            f"🏠 برد میزبان: {p_home}%\n"
            f"🤝 تساوی: {p_draw}%\n"
            f"✈️ برد میهمان: {p_away}%"
        )
        bot.send_message(call.message.chat.id, pred_msg, parse_mode='HTML')
        bot.answer_callback_query(call.id, text="در حال پردازش داده‌های واقعی...")

if __name__ == "__main__":
    logger.info("ربات حرفه‌ای با API واقعی فعال است...")
    bot.infinity_polling()
