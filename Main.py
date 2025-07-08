import logging
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import threading
import asyncio
import aiohttp

# ✅ Your bot token
BOT_TOKEN = "7866890680:AAfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"

# ✅ Flask app for health check
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def home():
    return "Dexmate AI Bot is running!"

# ✅ Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ✅ /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Python")], [KeyboardButton("Java")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Welcome to Dexmate AI!\nChoose your language:", reply_markup=markup)

# ✅ Text message handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "python" in text:
        await update.message.reply_text("You selected Python.")
    elif "java" in text:
        await update.message.reply_text("You selected Java.")
    else:
        await update.message.reply_text("Please choose a valid language.")

# ✅ Get ID command
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your Telegram ID: {update.effective_user.id}")

# ✅ Flask thread
def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# ✅ Main app
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", get_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start Flask in a new thread
    threading.Thread(target=run_flask).start()

    # Set webhook with correct API format
    async def set_webhook():
        webhook_url = f"https://dexmateai.onrender.com"
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(set_url) as resp:
                print(await resp.text())

    asyncio.run(set_webhook())
    app.run_polling()  # Optional backup if webhook fails