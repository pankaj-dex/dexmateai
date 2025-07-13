import os
import logging
import asyncio
import base64
from io import BytesIO
from typing import Optional
import httpx
from PIL import Image
import pytesseract
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
OPENROUTER_API_KEY = ('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')
MODEL = "openai/gpt-3.5-turbo"
MAX_MESSAGE_LENGTH = 4000  # Telegram message length limit
RATE_LIMIT = 5  # Messages per minute per user

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Rate limiting storage
user_message_count = {}

# === Utility Functions ===
def log_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by Updates."""
    logger.error(f'Update {update} caused error {context.error}')

async def is_rate_limited(user_id: int) -> bool:
    """Check if user has exceeded rate limit."""
    count = user_message_count.get(user_id, 0)
    if count >= RATE_LIMIT:
        return True
    user_message_count[user_id] = count + 1
    asyncio.create_task(reset_user_count(user_id))
    return False

async def reset_user_count(user_id: int):
    """Reset user's message count after a minute."""
    await asyncio.sleep(60)
    user_message_count[user_id] = 0

def split_long_message(text: str) -> list[str]:
    """Split long messages to comply with Telegram's length limit."""
    return [text[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]

# === AI Services ===
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
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return "⚠️ The AI service is currently unavailable. Please try again later."
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "❌ Failed to get AI response. Please try again."

async def generate_image(prompt: str) -> Optional[BytesIO]:
    """Generate image from text prompt with improved error handling."""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "stability-ai/sdxl",
            "prompt": f"High-quality digital art of {prompt}",
            "width": 1024,
            "height": 1024,
            "steps": 50
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

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    welcome_msg = """🤖 *Welcome to CodeMate AI Bot!* 🤖

I can help you with:
- Writing code
- Debugging errors
- Optimizing code
- Analyzing code from images
- Generating tech diagrams

*Commands:*
/start - Show this message
/help - Get help
/code [language] [description] - Generate code
/analyze - Analyze code from image

*Examples:*
`/code Python quick sort`
`/analyze` (with attached code image)"""
    
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages with rate limiting."""
    user_id = update.effective_user.id
    
    if await is_rate_limited(user_id):
        await update.message.reply_text("⚠️ Too many requests. Please wait a minute.")
        return
    
    user_text = update.message.text.lower()
    
    if 'generate image' in user_text:
        prompt = user_text.replace('generate image', '').strip()
        if not prompt:
            await update.message.reply_text("Please provide an image description after 'generate image'")
            return
            
        await update.message.reply_text("🎨 Generating your image...")
        image = await generate_image(prompt)
        
        if image:
            await update.message.reply_photo(
                InputFile(image, filename="generated.png"),
                caption=f"Generated from: '{prompt}'"
            )
        else:
            await update.message.reply_text("❌ Failed to generate image. Please try a different description.")
    else:
        reply = await get_ai_response(update.message.text)
        for chunk in split_long_message(reply):
            await update.message.reply_text(chunk)

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
    
    for chunk in split_long_message(reply):
        await update.message.reply_text(chunk)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages containing code."""
    try:
        user_id = update.effective_user.id
        if await is_rate_limited(user_id):
            await update.message.reply_text("⚠️ Too many requests. Please wait a minute.")
            return
            
        await update.message.reply_text("🔍 Analyzing code from image...")
        
        # Get highest resolution photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()
        
        # Preprocess image for better OCR
        image = Image.open(BytesIO(photo_bytes))
        image = image.convert('L')  # Convert to grayscale
        image = image.point(lambda x: 0 if x < 128 else 255, '1')  # Increase contrast
        
        # Extract text with pytesseract
        text = pytesseract.image_to_string(image)
        
        if not text.strip():
            raise ValueError("No text detected in image")
            
        # Determine if it's an error or code analysis
        if any(word in text.lower() for word in ['error', 'exception', 'traceback']):
            prompt = f"Debug this code error:\n\n{text}\n\nProvide:\n1. Error cause\n2. Fixed code\n3. Prevention tips"
        else:
            prompt = f"Analyze this code:\n\n{text}\n\nProvide:\n1. Purpose\n2. Issues\n3. Improvements\n4. Security checks"
        
        reply = await get_ai_response(prompt, is_code=True)
        
        for chunk in split_long_message(reply):
            await update.message.reply_text(chunk)
            
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        await update.message.reply_text("❌ Failed to analyze the image. Please ensure it contains clear, readable code.")

# === Bot Setup ===
async def run_bot():
    """Run the bot with proper webhook or polling setup."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("code", handle_code_command))
    app.add_handler(CommandHandler("analyze", handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_error_handler(log_error)
    
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