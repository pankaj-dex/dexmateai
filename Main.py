import logging
import asyncio
import threading
from flask import Flask, request

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)

# ✅ Your bot token
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"

# ✅ Flask app
app_flask = Flask(__name__)

# ✅ Create Application (but not yet initialized)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# ✅ Home route
@app_flask.route("/", methods=["GET"])
def home():
    return "✅ Dexmate AI Bot is running!"

# ✅ Telegram webhook receiver
@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    # 👉 Must use initialized application!
    asyncio.run(handle_update(update))
    return "OK", 200

# ✅ Handler to safely process update
async def handle_update(update: Update):
    if not bot_app._initialized:
        await bot_app.initialize()
    await bot_app.process_update(update)

# ✅ Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Python")], [KeyboardButton("Java")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Welcome to Dexmate AI!\nChoose your language:",
        reply_markup=markup
    )

# ✅ Text message handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "python" in text:
        await update.message.reply_text("🐍 You chose Python!")
    elif "java" in text:
        await update.message.reply_text("☕ You chose Java!")
    else:
        await update.message.reply_text("❗ Please choose Python or Java.")

# ✅ Add handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# ✅ Run Flask server in background
def run_flask():
    app_flask.run(host="0.0.0.0", port=8080)

# ✅ Main async runner
async def main():
    await bot_app.initialize()  # Required!
    await bot_app.bot.set_webhook(f"https://dexmateai.onrender.com/{BOT_TOKEN}")
    print("✅ Webhook set. Bot is ready!")

# ✅ Run both Flask and Telegram initialization
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(main())