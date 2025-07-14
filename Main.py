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
    """Get response from AI with enhanced error handling."""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "❌ Failed to get AI response. Please try again."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message."""
    welcome_msg = """🤖 *Welcome to CodeMate AI Bot!* 🤖

I can help you with:
- Writing code
- Debugging errors
- Optimizing code
- Explaining concepts

*Commands:*
/start - Show this message
/code [language] [description] - Generate code

*Examples:*
`/code Python quick sort`"""
    
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

async def handle_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /code command for generating code."""
    if not context.args:
        await update.message.reply_text("Usage: /code [language] [description]\nExample: /code Python quick sort")
        return
    
    language = context.args[0]
    description = ' '.join(context.args[1:])
    prompt = f"Write {language} code for: {description}\n\nProvide:\n1. Complete implementation\n2. Brief explanation\n3. Usage example"
    
    await update.message.reply_text(f"💻 Generating {language} code for: {description}...")
    reply = await get_ai_response(prompt)
    await update.message.reply_text(reply)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    reply = await get_ai_response(update.message.text)
    await update.message.reply_text(reply)

async def run_bot():
    """Run the bot with proper webhook or polling setup."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("code", handle_code_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Production (Render) vs Development setup
    if os.getenv('ENVIRONMENT') == 'production':
        WEBHOOK_URL = os.getenv('WEBHOOK_URL')
        await app.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
        logger.info("Bot started with webhook")
    else:
        await app.run_polling()
        logger.info("Bot started with polling")

if __name__ == '__main__':
    asyncio.run(run_bot())