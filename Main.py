import os 
import logging
import asyncio from flask import Flask,
request 
from telegram import Update,
Bot from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters import openai

#=== CONFIGURATION ===

BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA" OPENAI_API_KEY = "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" WEBHOOK_URL = "https://dexmateai.onrender.com/" + BOT_TOKEN

#=== LOGGING ===

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

#=== FLASK APP ===

app = Flask(name)

#=== OPENAI ===

openai.api_key = OPENAI_API_KEY

#== TELEGRAM APPLICATION ===

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

#=== MESSAGE HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_message = update.message.text.strip() user_id = update.message.from_user.id

# Reply to greetings
if user_message.lower() in ["hello", "hi", "hey"]:
    await update.message.reply_text("How are you? Do you need any help? How can I help you?")
    return

# Respond with AI-generated answer
await update.message.reply_text("⏳ Let me think...")
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    answer = response.choices[0].message.content.strip()
    await update.message.reply_text(answer)
except Exception as e:
    await update.message.reply_text("❌ Sorry, something went wrong while generating the response.")
    logger.error(f"OpenAI Error: {e}")

bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#= FLASK ROUTES ===

@app.route(f"/{BOT_TOKEN}", methods=["POST"]) def receive_update(): update = Update.de_json(request.get_json(force=True), bot_app.bot) asyncio.run(bot_app.process_update(update)) return "OK"

@app.route("/") def index(): return "🤖 Dexmate AI Bot is Live!"

#== MAIN ===

if name == 'main': async def set_webhook(): bot = Bot(token=BOT_TOKEN) await bot.set_webhook(WEBHOOK_URL) logger.info("✅ Webhook set. Bot is ready!")

asyncio.run(set_webhook())
logger.info("✅ Bot is Live on Render!")
app.run(host="0.0.0.0", port=10000)

