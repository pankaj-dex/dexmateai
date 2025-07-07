from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "6531365793:AAHQ7ZIQiMrPY5eZMbUhy5AlpkKkI0NpiYA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Dexmate AI is working perfectly!")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url="https://dexmateai.onrender.com"
    )

if __name__ == "__main__":
    main()