import os
import logging
import asyncio
import base64
import tempfile
import httpx
from io import BytesIO
from flask import Flask
from PIL import Image
import pytesseract
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    ContextTypes, filters
)

# === CONFIG ===
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"

def log_error(update, context):
    logging.error(f"Update {update} caused error {context.error}")

# === AI RESPONSE ===
async def get_ai_response(prompt):
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
            response = await client.post("https://openrouter.ai/api/v1/chat/completions",
                                         headers=headers, json=payload)
            data = response.json()
            return data['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"AI error: {e}")
        return "❌ AI failed to respond."

# === IMAGE GENERATION ===
async def generate_image(prompt: str) -> BytesIO:
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "stability-ai/sdxl",
            "prompt": prompt
        }
        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/generate", headers=headers, json=payload)
            if response.status_code != 200:
                raise Exception("Image generation failed")
            data = response.json()
            image_data = base64.b64decode(data['image_base64'])
            return BytesIO(image_data)
    except Exception as e:
        logging.error(f"Image generation error: {e}")
        return None

# === TEXT HANDLER ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    if 'generate image' in user_text:
        prompt = user_text.replace('generate image', '').strip()
        await update.message.reply_text("🖼 Generating image...")
        image = await generate_image(prompt)
        if image:
            await update.message.reply_photo(InputFile(image, filename="generated.png"))
        else:
            await update.message.reply_text("❌ Failed to generate image.")
    else:
        reply = await get_ai_response(update.message.text)
        await update.message.reply_text(reply)

# === IMAGE UPLOAD ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()
        image = Image.open(BytesIO(photo_bytes))
        text = pytesseract.image_to_string(image)

        if "error" in text.lower() or "exception" in text.lower():
            prompt = f"Please fix this code error from image:
{text}"
        else:
            prompt = f"Analyze the following code extracted from an image and provide suggestions or improvements:
{text}"

        reply = await get_ai_response(prompt)
        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Image error: {e}")
        await update.message.reply_text("❌ Failed to read the image or analyze code.")

# === MAIN FUNCTION ===
async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_error_handler(log_error)

    print("✅ Telegram bot started...")
    await app.run_polling()

# === FLASK KEEP-ALIVE ===
app_flask = Flask(__name__)

@app_flask.route('/')
def index():
    return "Dexmate AI is running ✅"

# === START ===
if __name__ == '__main__':
    import threading

    def start():
        asyncio.run(run_bot())

    threading.Thread(target=start).start()
    app_flask.run(host='0.0.0.0', port=10000)
