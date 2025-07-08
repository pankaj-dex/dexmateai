import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import threading
import asyncio

# Bot token (already filled)
BOT_TOKEN = "7866890680:AAfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"

# Flask app setup
app_flask = Flask(__name__)

@app_flask.route("/", methods=["GET"])
def home():
    return "Dexmate AI Bot is running!"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Python")], [KeyboardButton("Java")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Welcome to Dexmate AI!\nChoose your language:", reply_markup=markup
    )

# handle user text replies
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "python" in text:
        await update.message.reply_text("You chose Python. How can I help?")
    elif "java" in text:
        await update.message.reply_text("You chose Java. What's your query?")
    else:
        await update.message.reply_text("Please choose a valid language.")

# getid command
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your ID is: {update.effective_user.id}")

# run flask in background thread
def run_flask():
    app_flask.run(host="0.0.0.0", port=8080)

# Main app
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", get_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    threading.Thread(target=run_flask).start()

    asyncio.run(app.bot.set_webhook("https://dexmateai.onrender.com/" + BOT_TOKEN))
    app.run_polling()  # Optional backup for local testing (not needed on Render)