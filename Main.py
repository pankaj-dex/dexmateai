import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import openai
import httpx

# 🧠 CONFIG
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENAI_API_KEY = "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"
WEBHOOK_URL = "https://dexmateai.onrender.com/" + BOT_TOKEN

# 🔧 LOGGING
logging.basicConfig(level=logging.INFO)

# 🤖 INIT
app = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# 🤖 BOT LOGIC
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()
    user = update.effective_user.first_name

    if any(word in message for word in ["hello", "hi", "hey"]):
        await update.message.reply_text("How are you? Do you need any help? How can I help you?")
    else:
        try:
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": update.message.text}],
                max_tokens=150,
                temperature=0.7,
            )
            reply = response['choices'][0]['message']['content']
            await update.message.reply_text(reply)
        except Exception as e:
            await update.message.reply_text("⚠️ Sorry, I couldn’t process that. Please try again later.")

# 🔌 ADD HANDLER
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 🌐 WEBHOOK ENDPOINT
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.initialize())  # REQUIRED
    asyncio.run(bot_app.process_update(update))
    return "OK"

# 🧪 HEALTH CHECK
@app.route("/", methods=["GET"])
def index():
    return "🤖 Dexmate AI is running."

# 🔥 MAIN START
if __name__ == "__main__":
    async def setup():
        async with httpx.AsyncClient() as client:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
            data = {"url": WEBHOOK_URL}
            r = await client.post(url, json=data)
            print("✅ Webhook set. Bot is ready!" if r.status_code == 200 else "❌ Failed to set webhook")
        await bot_app.initialize()
    asyncio.run(setup())
    logging.info("✅ Bot is Live on Render!")
    app.run(host="0.0.0.0", port=10000)