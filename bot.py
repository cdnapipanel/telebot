import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. دریافت توکن‌ها از Secretهای گیت‌هاب
BOT_TOKEN = os.getenv('BOT_TOKEN')
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')

BASE_URL = "https://api.football-data.org/v4"

# شناسه لیگ‌ها (Competition IDs)
LEAGUES = {
    'PL': 'PL',       # Premier League
    'LL': 'PD',       # La Liga
    'SA': 'SA',       # Serie A
    'BL': 'BL1',      # Bundesliga
    'FL1': 'FL1'      # Ligue 1
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    help_text = (
        "👋 سلام! من ربات فوتبالی هستم.\n\n"
        "🔹 دستورات موجود:\n"
        "/match [لیگ] - بازی‌های آینده (مثال: /match PL)\n"
        "/standings [لیگ] - جدول لیگ (مثال: /standings LL)\n"
        "\n🏆 لیگ‌های پشتیبانی شده:\n"
        "PL: لیگ برتر انگلیس\nLL: لالیگا اسپانیا\nSA: سری آ ایتالیا\nBL: بوندسلیگا آلمان\nFL1: لیگ ۱ فرانسه"
    )
    await update.message.reply_text(help_text)

async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /match - نمایش بازی‌های آینده"""
    try:
        # دریافت نام لیگ از آرگومان دستور
        league_code = context.args[0].upper() if context.args else None
        
        if league_code and league_code not in LEAGUES:
            await update.message.reply_text("❌ لیگ معتبر نیست. لطفاً از کدهای زیر استفاده کنید: PL, LL, SA, BL, FL1")
            return

        # ساخت URL بر اساس لیگ انتخابی
        url = f"{BASE_URL}/matches?status=SCHEDULED"
        if league_code:
            url += f"&competitions={LEAGUES[league_code]}"

        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            if not matches:
                msg = "هیچ بازی برنامه‌ریزی شده‌ای یافت نشد."
                if league_code:
                    msg += f"\n(برای لیگ {context.args[0]})"
                await update.message.reply_text(msg)
                return

            display_matches = matches[:5] # نمایش 5 بازی اول
            msg = "🔥 بازی‌های پیش‌رو:\n\n"
            for m in display_matches: 
                home = m['homeTeam']['name']
                away = m['awayTeam']['name']
                time = m['utcDate']
                comp_name = m['competition']['name']
                
                # اگر لیگ خاصی درخواست نشده بود، اسم لیگ را هم بنویسیم
                league_info = f"[{comp_name}] " if not league_code else ""
                
                msg += f"{league_info}⚽ {home} vs {away}\n⏰ {time}\n\n"
            
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text(f"خطا در ارتباط با سرور فوتبال: {response.status_code}")
            
    except IndexError:
        await update.message.reply_text("لطفاً نام لیگ را مشخص کنید. مثال: `/match PL`")
    except Exception as e:
        await update.message.reply_text(f"خطا: {str(e)}")

async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /standings - نمایش جدول لیگ"""
    try:
        league_code = context.args[0].upper() if context.args else None
        
        if not league_code or league_code not in LEAGUES:
            await update.message.reply_text("❌ لطفاً کد لیگ را وارد کنید. مثال: `/standings PL`")
            return

        url = f"{BASE_URL}/competitions/{LEAGUES[league_code]}/standings"
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            standings_list = data.get('standingTable', {}).get('standings', [{}])[0].get('table', [])
            
            if not standings_list:
                await update.message.reply_text("جدولی برای این لیگ یافت نشد.")
                return

            msg = f"📊 جدول لیگ {data['standingTable'].get('team', {}).get('name', 'Unknown')} (۱۰ تیم اول):\n\n"
            
            for entry in standings_list[:10]:
                team = entry['team']['name']
                played = entry['playedGames']
                won = entry['won']
                draw = entry['draw']
                lost = entry['lost']
                points = entry['points']
                pos = entry['position']
                
                msg += f"{pos}. {team} | امتیاز: {points} | برد: {won} | مساوی: {draw} | باخت: {lost}\n"
            
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text(f"خطا در دریافت جدول: {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"خطا: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('match', match))
    app.add_handler(CommandHandler('standings', standings))
    
    print("ربات در حال اجراست... (برای خروج Ctrl+C بزنید)")
    app.run_polling()

if __name__ == '__main__':
    main()
