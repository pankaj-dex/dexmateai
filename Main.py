import os
import logging
import openai
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Load secrets
BOT_TOKEN = os.getenv("BOT_TOKEN", "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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").strip()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://dexmateai.onrender.com/webhook").strip()

# Init Flask and Logger
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Init Telegram Application
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Message Handling
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.lower()

    if "hello" in user_msg or "hi" in user_msg:
        reply = "How are you? Do you need any help? How can I help you?"
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": update.message.text}]
            )
            reply = response['choices'][0]['message']['content']
        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            reply = "Sorry, something went wrong while generating the answer."

    await update.message.reply_text(reply)

# Register handler
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route for webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        asyncio.run(bot_app.process_update(update))
        return "ok"
    return "invalid"

# Root route
@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

# Set webhook and run
if __name__ == "__main__":
    bot = Bot(BOT_TOKEN)
    asyncio.run(bot.set_webhook(url=WEBHOOK_URL + "/webhook"))
    logging.info("✅ Webhook set. Bot is ready!")
    logging.info("✅ Bot is Live on Render!")
    app.run(host="0.0.0.0", port=10000)