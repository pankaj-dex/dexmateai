import logging
import asyncio
import threading
from flask import Flask, request

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)

# ✅ Bot Token
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"

# ✅ Flask App
app_flask = Flask(__name__)

@app_flask.route("/", methods=["GET"])
def home():
    return "✅ Dexmate AI Bot is running!"

# ✅ Telegram webhook route to receive updates
@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.process_update(update))
    return "OK", 200

# ✅ Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ✅ /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Python")], [KeyboardButton("Java")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Welcome to Dexmate AI!\nChoose your language:",
        reply_markup=markup
    )

# ✅ Message handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "python" in text:
        await update.message.reply_text("🧠 You chose Python!")
    elif "java" in text:
        await update.message.reply_text("☕ You chose Java!")
    else:
        await update.message.reply_text("Please choose a valid option.")

# ✅ Build the bot app
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# ✅ Function to run Flask server
def run_flask():
    app_flask.run(host="0.0.0.0", port=8080)

# ✅ Main entry
if __name__ == "__main__":
    # Start Flask server in a new thread
    threading.Thread(target=run_flask).start()

    # Set webhook and run the app
    async def main():
        await bot_app.bot.set_webhook(f"https://dexmateai.onrender.com/{BOT_TOKEN}")
        print("✅ Webhook set successfully.")

    asyncio.run(main())