import logging
import os
import httpx
import base64
import io

from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CommandHandler,
    filters,
)

# === CONFIG ===
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === FLASK SETUP ===
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Dexmate AI Bot is Running ✅"

# === OPENROUTER TEXT COMPLETION ===
async def get_ai_response(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        json_data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=json_data)
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"AI error: {e}")
        return "❌ Failed to generate AI response."

# === IMAGE TO TEXT / ERROR CHECKING ===
async def analyze_image_for_code(image_bytes):
    try:
        base64_img = base64.b64encode(image_bytes).decode()
        prompt = f"This is a screenshot of some code. Identify mistakes or bugs and suggest improvements:\n[Image base64 below]\n{base64_img[:10000]}"
        return await get_ai_response(prompt)
    except Exception as e:
        return "❌ Error analyzing image."

# === IMAGE GENERATION ===
async def generate_image_from_prompt(prompt_text):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "stabilityai/stable-diffusion-512-v2-1",
            "prompt": prompt_text
        }
        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/generate", json=payload, headers=headers)
            data = response.json()
            if 'image' in data:
                return base64.b64decode(data['image'])
            return None
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return None

# === TELEGRAM HANDLERS ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if "generate image" in user_text.lower():
        prompt = user_text.replace("generate image", "").strip()
        await update.message.reply_text("🎨 Generating image...")
        image_data = await generate_image_from_prompt(prompt)
        if image_data:
            await update.message.reply_photo(photo=io.BytesIO(image_data))
        else:
            await update.message.reply_text("❌ Failed to generate image.")
    else:
        ai_response = await get_ai_response(user_text)
        await update.message.reply_text(ai_response)

async def handle_document_or_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1]
    file_id = file.file_id
    new_file = await context.bot.get_file(file_id)
    file_bytes = await new_file.download_as_bytearray()
    await update.message.reply_text("🔍 Analyzing your file...")
    response = await analyze_image_for_code(file_bytes)
    await update.message.reply_text(response)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice received! Voice-to-text feature coming soon.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Dexmate AI! How can I assist you today?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 Send me a question or image and I'll try to help with AI.\nYou can also type 'generate image <your prompt>' to create art!")

# === ERROR HANDLER ===
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update.message:
        await update.message.reply_text("⚠️ Sorry, something went wrong!")

# === RUN BOT ===
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document_or_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_error_handler(error_handler)
    app.run_polling()

# === MAIN ===
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    flask_app.run(host="0.0.0.0", port=10000)