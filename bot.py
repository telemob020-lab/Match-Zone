import os
import requests

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

API_URL = "https://v3.football.api-sports.io"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚽ مباريات اليوم", callback_data="today_matches")],
        [InlineKeyboardButton("🏆 تحدي اليوم", callback_data="daily_challenge")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚽ أهلاً بك في Match Zone!\n\n"
        "تابع المباريات واختبر معلوماتك الرياضية 👇",
        reply_markup=reply_markup,
    )


async def get_today_matches():
    response = requests.get(
        f"{API_URL}/fixtures",
        params={"date": "2026-08-16"},
        headers={"x-apisports-key": API_FOOTBALL_KEY},
        timeout=15,
    )

    response.raise_for_status()
    return response.json()


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "today_matches":
        await query.edit_message_text("⏳ جاري جلب مباريات اليوم...")

        try:
            data = await get_today_matches()
            matches = data.get("response", [])

            if not matches:
                await query.edit_message_text(
                    "⚽ لا توجد مباريات متاحة اليوم."
                )
                return

            text = "⚽ مباريات اليوم\n\n"

            for match in matches[:15]:
                home = match["teams"]["home"]["name"]
                away = match["teams"]["away"]["name"]
                league = match["league"]["name"]

                text += (
                    f"🏆 {league}\n"
                    f"⚽ {home} × {away}\n\n"
                )

            await query.edit_message_text(text)

        except Exception as e:
            print("ERROR:", e)

            await query.edit_message_text(
                "❌ حصل خطأ أثناء جلب المباريات.\n"
                "تأكد من إعداد API Key بشكل صحيح."
            )

    elif query.data == "daily_challenge":
        await query.edit_message_text(
            "🏆 تحدي اليوم\n\n"
            "من هو أكثر لاعب سجل أهدافًا في تاريخ دوري أبطال أوروبا؟\n\n"
            "🔜 هنضيف الاختيارات في الخطوة القادمة."
        )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN غير موجود في ملف .env")

    if not API_FOOTBALL_KEY:
        raise ValueError("API_FOOTBALL_KEY غير موجود في ملف .env")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Match Zone is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
