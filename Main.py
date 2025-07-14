import os
import logging
import asyncio
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

# Configuration
BOT_TOKEN = os.getenv('7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA')
OPENROUTER_API_KEY = os.getenv('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')
MODEL = "openai/gpt-3.5-turbo"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def get_ai_response(prompt: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "❌ Failed to process your request. Please try again."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *CodeMate AI Bot*\n\n"
        "I can help with:\n"
        "- Writing code\n- Debugging\n- Code reviews\n\n"
        "Just send me your code questions!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = await get_ai_response(update.message.text)
    await update.message.reply_text(reply)

async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    if os.getenv('ENVIRONMENT') == 'production':
        await app.bot.set_webhook(f"{os.getenv('WEBHOOK_URL')}/{BOT_TOKEN}")
        logger.info("Webhook configured")
    else:
        await app.run_polling()
        logger.info("Polling started")

if __name__ == '__main__':
    asyncio.run(run_bot())