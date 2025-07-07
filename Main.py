from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"

WEBHOOK_URL = "https://dexmateai.onrender.com/webhook"  # Replace with your actual Render URL if different

app = Flask(__name__)

# ====== Telegram Bot Handler ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Dexmate AI is Live. How can I help you?")

# ====== Set up Telegram Application ======
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# ====== Webhook Endpoint ======
@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "OK"

# ====== Homepage Endpoint ======
@app.route('/')
def home():
    return "🤖 Dexmate AI Bot is Running via Webhook!"

# ====== Run Locally (Not used on Render) ======
if __name__ == "__main__":
    application.run_polling()