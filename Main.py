
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ==== Fill These ====
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
WEBHOOK_URL = f"https://dexmateai.onrender.com/{BOT_TOKEN}"
# ====================

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Create Telegram application
bot_app = Application.builder().token(BOT_TOKEN).build()


# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I’m Dexmate AI. How can I help you?")

async def reply_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")


# Add handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_all))


# --- Flask route for webhook ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.initialize())
    asyncio.run(bot_app.process_update(update))
    return "OK"


# --- Home route ---
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "Dexmate AI Bot is Live!"

# --- Start the Flask app ---
if __name__ == "__main__":
    async def set_webhook():
        await bot_app.bot.set_webhook(WEBHOOK_URL)
        logger.info("✅ Webhook set. Bot is ready!")

    asyncio.run(set_webhook())
    logger.info("✅ Bot is Live on Render!")
    app.run(host="0.0.0.0", port=10000)