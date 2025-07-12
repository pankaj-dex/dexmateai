import logging
import httpx
import base64
import io
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

# === CONFIG ===
BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA"
OPENROUTER_API_KEY = "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"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === FLASK APP ===
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Dexmate AI Bot is Live!"

# === AI TEXT REPLY ===
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
        return "❌ Failed to get AI response."

# === IMAGE ANALYSIS (CODE CHECK) ===
async def analyze_image_for_code(image_bytes):
    base64_img = base64.b64encode(image_bytes).decode()
    prompt = f"This is a screenshot of code. What mistakes can you find?\n{base64_img[:10000]}"
    return await get_ai_response(prompt)

# === IMAGE GENERATION ===
async def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "stabilityai/stable-diffusion-512-v2-1",
        "prompt": prompt
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("https://openrouter.ai/api/v1/generate", json=payload, headers=headers)
        if "image" in response.json():
            return base64.b64decode(response.json()["image"])
        return None

# === TELEGRAM HANDLERS ===
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "generate image" in text.lower():
        prompt = text.replace("generate image", "").strip()
        await update.message.reply_text("🎨 Generating image...")
        img = await generate_image(prompt)
        if img:
            await update.message.reply_photo(photo=io.BytesIO(img))
        else:
            await update.message.reply_text("❌ Image generation failed.")
    else:
        reply = await get_ai_response(text)
        await update.message.reply_text(reply)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1]
    file_data = await context.bot.get_file(file.file_id)
    image_bytes = await file_data.download_as_bytearray()
    await update.message.reply_text("🧠 Analyzing your image/code...")
    result = await analyze_image_for_code(image_bytes)
    await update.message.reply_text(result)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 Voice feature coming soon.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm Dexmate AI. Send a message or image and I’ll help you!")

# === ERROR HANDLER ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Sorry, something went wrong.")

# === TELEGRAM BOT ===
async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    await application.run_polling()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_error_handler(error_handler)
    await app.run_polling()

# === MAIN ===
if __name__ == "__main__":
    import threading

    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=10000)).start()
    asyncio.run(run_bot())