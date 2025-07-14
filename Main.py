import os
import logging
import asyncio
import base64
from io import BytesIO
import httpx
from PIL import Image
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

# === Configuration ===
BOT_TOKEN = os.getenv('7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA')
OPENROUTER_API_KEY = os.getenv('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')
MODEL = "openai/gpt-3.5-turbo"
MAX_MESSAGE_LENGTH = 4000  # Telegram message length limit

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === AI Service Functions ===
async def get_ai_response(prompt: str, is_code: bool = False) -> str:
    """Get response from AI with enhanced error handling."""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Customize prompt for code analysis
        if is_code:
            prompt = f"""Please analyze this code:
{prompt}

Provide:
1. Purpose/functionality
2. Potential bugs/issues
3. Optimization suggestions
4. Security considerations
5. Improved version (if needed)"""

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
            
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "❌ Failed to get AI response. Please try again."

async def generate_image(prompt: str) -> BytesIO:
    """Generate image from text prompt."""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "stability-ai/sdxl",
            "prompt": f"High-quality digital art of {prompt}",
            "width": 1024,
            "height": 1024
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/generate",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            image_data = base64.b64decode(data['image_base64'])
            return BytesIO(image_data)
            
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None

# === Message Handlers ===
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
/image [description] - Generate tech diagram

*Examples:*
`/code Python quick sort`
`/image database architecture diagram`"""
    
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
    reply = await get_ai_response(prompt, is_code=True)
    await update.message.reply_text(reply)

async def handle_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /image command for generating diagrams."""
    if not context.args:
        await update.message.reply_text("Usage: /image [description]\nExample: /image database architecture diagram")
        return
    
    prompt = ' '.join(context.args)
    await update.message.reply_text("🎨 Generating your diagram...")
    image = await generate_image(prompt)
    
    if image:
        await update.message.reply_photo(
            InputFile(image, filename="diagram.png"),
            caption=f"Diagram: {prompt}"
        )
    else:
        await update.message.reply_text("❌ Failed to generate image. Please try a different description.")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    user_text = update.message.text.lower()
    
    # Check for code-related keywords
    if any(keyword in user_text for keyword in ['fix code', 'debug', 'error in']):
        prompt = f"Help fix this code issue:\n\n{update.message.text}"
        reply = await get_ai_response(prompt, is_code=True)
    else:
        reply = await get_ai_response(update.message.text)
    
    await update.message.reply_text(reply)

# === Bot Setup ===
async def run_bot():
    """Run the bot with proper webhook or polling setup."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("code", handle_code_command))
    app.add_handler(CommandHandler("image", handle_image_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
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