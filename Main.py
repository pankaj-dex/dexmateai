import os
import logging
import asyncio
import openai
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)

# Set your bot token and OpenAI API key
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global bot app instance
bot_app = None

# Core AI reply handler
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if user_message.lower() in ["hello", "hi", "hey"]:
        await update.message.reply_text("How are you? Do you need any help? How can I help you?")
    else:
        try:
            # Call OpenAI to get a response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant who replies to coding and programming questions for free."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response["choices"][0]["message"]["content"]
            await update.message.reply_text(reply)
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            await update.message.reply_text("❌ Sorry, I couldn't process your request right now.")

# Webhook endpoint for Telegram
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    from telegram import Update
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.process_update(update))
    return "OK"

# Home route
@app.route('/')
def home():
    return "🤖 Dexmate AI Bot is Live!"

# Main startup
if __name__ == "__main__":
    async def main():
        global bot_app
        bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

        # Set webhook
        url = f"https://dexmateai.onrender.com/{BOT_TOKEN}"
        await bot_app.bot.set_webhook(url)

        logger.info("✅ Webhook set. Bot is ready!")

    asyncio.run(main())
    logger.info("✅ Bot is Live on Render!")
    app.run(host="0.