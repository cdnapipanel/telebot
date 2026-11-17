import asyncio
from pyrogram import Client, filters
from datetime import datetime

# تنظیمات
API_ID = "1769845"
API_HASH = "0daad38509d4718ebecff0dc650f9f3e"
BOT_TOKEN = "9226904032:AAHcCU-I6CY0YTT2xk9WQol0vf3md3VzpTM"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def update_profile_name():
    while True:
        try:
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            new_name = f"MyProfile | {time_str} 🤖"
            await app.set_username(new_name)
            print(f"[{time_str}] Profile name updated to: {new_name}")
        except Exception as e:
            print(f"Error updating profile: {e}")
        await asyncio.sleep(5)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("سلام! من یک هوش مصنوعی هستم.")

async def main():
    await app.start()
    print("ربات شروع به کار کرد!")
    
    # اجرای همزمان
    listen_task = asyncio.create_task(app.run())
    update_task = asyncio.create_task(update_profile_name())
    
    try:
        await asyncio.gather(listen_task, update_task)
    finally:
        await app.stop()

if __name__ == "__main__":
    # این خط مشکل پایتون ۳.۱۴ را حل می‌کند
    asyncio.run(main())
