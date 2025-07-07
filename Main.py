from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import asyncio

app = Flask(__name__)

# Fill your token here
BOT_TOKEN = "6531365793:AAHQ7ZIQiMrPY5eZMbUhy5AlpkKkI0NpiYA"

application = ApplicationBuilder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Dexmate AI is live!")

# Register handlers
application.add_handler(CommandHandler("start", start))

# Telegram webhook handler
@app.route("/", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
    return "ok"

# Health check
@app.route("/", methods=["GET"])
def index():
    return "Dexmate AI running!"

if __name__ == "__main__":
    # Set the webhook (you only need to do this once)
    import requests
    webhook_url = "https://dexmateai.onrender.com"
    set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    print("Setting webhook:", requests.get(set_url).text)

    app.run(host="0.0.0.0", port=10000)