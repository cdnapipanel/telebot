import os
import requests
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, filters

# تنظیمات اولیه
BOT_TOKEN = os.getenv('BOT_TOKEN')
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://api.football-data.org/v4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پیام خوش‌آمدگویی"""
    welcome_msg = (
        "👋 سلام! من دستیار هوشمند فوتبال هستم.\n\n"
        "🔹 دستورالعمل‌ها:\n"
        "• `/match [لیگ]` : نمایش بازی‌های آینده (مثال: /match PL)\n"
        "• `/standings [لیگ]` : جدول رده‌بندی (مثال: /standings PD)\n"
        "• `/start` : شروع مجدد\n\n"
        "🏆 لیگ‌های محبوب: PL (انگلستان), PD (اسپانیا), SA (ایتالیا), BL1 (آلمان), FL1 (فرانسه), BSA (برزیل)"
    )
    await update.message.reply_text(welcome_msg)

async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت بازی‌های آینده"""
    # دریافت کد لیگ از آرگومان‌ها
    league_code = context.args[0].upper() if context.args else None
    
    # ساخت URL پایه
    url = f"{BASE_URL}/matches?status=SCHEDULED&timeFrame=next7d"
    
    # اضافه کردن فیلتر لیگ در صورت وجود
    if league_code:
        url += f"&competitions={league_code}"

    try:
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            
            if not matches:
                msg = f"✅ هیچ بازی برنامه‌ریزی شده‌ای برای {league_code or 'همه لیگ‌ها'} یافت نشد."
                await update.message.reply_text(msg)
                return

            # انتخاب ۵ بازی اول
            display_matches = matches[:5]
            msg = "⚽ **بازی‌های پیش‌رو (۷ روز آینده):**\n\n"
            
            for m in display_matches: 
                home = m['homeTeam']['name']
                away = m['awayTeam']['name']
                time = m['utcDate']
                comp_name = m['competition']['name']
                
                # فرمت‌بندی پیام
                msg += f"🏠 **{home}** vs **{away}**\n"
                msg += f"📅 تاریخ: `{time}`\n"
                msg += f"🏆 لیگ: *{comp_name}*\n\n"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
            
        elif response.status_code == 401:
            await update.message.reply_text("❌ خطا: توکن API نامعتبر است.")
        elif response.status_code == 404:
            await update.message.reply_text(f"❌ لیگ با کد `{league_code}` یافت نشد.")
        else:
            await update.message.reply_text(f"❌ خطا در ارتباط با سرور: {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا: {str(e)}")

async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت جدول لیگ"""
    league_code = context.args[0].upper() if context.args else None
    
    if not league_code:
        await update.message.reply_text("لطفاً کد لیگ را وارد کنید. مثال: `/standings PL`")
        return

    url = f"{BASE_URL}/competitions/{league_code}/standings"
    
    try:
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            table_data = data.get('standingTable', {}).get('standings', [{}])[0].get('table', [])
            
            if not table_data:
                await update.message.reply_text("جدولی یافت نشد.")
                return

            msg = f"📊 **جدول {data['standingTable'].get('team', {}).get('name', '')}**\n\n"
            
            # نمایش ۱۰ تیم اول
            for entry in table_data[:10]:
                team = entry['team']['name']
                pts = entry['points']
                pos = entry['position']
                played = entry['playedGames']
                won = entry['won']
                draw = entry['draw']
                lost = entry['lost']
                
                msg += f"{pos}. {team} | امتیاز: {pts} | B:{won} M:{draw} X:{lost}\n"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
            
        else:
            await update.message.reply_text(f"❌ خطا: {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا: {str(e)}")

def main():
    # بررسی وجود توکن‌ها قبل از اجرا
    if not BOT_TOKEN or not FOOTBALL_API_KEY:
        print("خطا: لطفاً BOT_TOKEN و FOOTBALL_API_KEY را در Secretها تنظیم کنید.")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    
    # تعریف دستورات
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('match', match))
    app.add_handler(CommandHandler('standings', standings))
    
    print("🤖 ربات فعال و آماده کار است...")
    app.run_polling()

if __name__ == '__main__':
    main()
