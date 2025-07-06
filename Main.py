from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import logging

# ✅ Replace this with your bot token
BOT_TOKEN = "6531365793:AAHQ7ZIQiMrPY5eZMbUhy5AlpkKkI0NpiYA"

# ✅ Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Dexmate AI is live and working!")

# ✅ Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # ✅ For Render deployment, use webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url="https://dexmateai.onrender.com/"
    )

if __name__ == '__main__':
    main()