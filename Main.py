#Dexmate AI - Production-Ready Telegram Bot

#Version: Free until 16 August | Built to scale | Easy to update

from flask import Flask, request from telegram import Update, Bot from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters import openai import logging import asyncio import os

#=== CONFIGURATION ===

BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA" OPENROUTER_API_KEY = "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" BOT_USERNAME = "Dex_Ai_coderbot" BASE_URL = f"https://dexmateai.onrender.com/{BOT_TOKEN}"

#=== LOGGING ===

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

#=== FLASK SETUP ===

app = Flask(name)

#=== GPT-4 API Function ===

async def get_ai_reply(prompt): try: import httpx headers = { "Authorization": f"Bearer {OPENROUTER_API_KEY}", "HTTP-Referer": "https://chat.openai.com", "X-Title": "Dexmate AI" } payload = { "model": "openrouter/openai/gpt-4", "messages": [ {"role": "user", "content": prompt} ] } async with httpx.AsyncClient() as client: response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers) return response.json()["choices"][0]["message"]["content"] except Exception as e: return "⚠️ Sorry, I couldn't process your request. Please try again later."

#=== MESSAGE HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_message = update.message.text.strip().lower() if user_message in ["hello", "hi", "hey"]: await update.message.reply_text("👋 How are you? Do you need any help? How can I help you?") else: await update.message.reply_text("🧠 Thinking... Please wait.") reply = await get_ai_reply(update.message.text) await update.message.reply_text(reply)

#=== TELEGRAM SETUP ===

bot_app = ApplicationBuilder().token(BOT_TOKEN).build() bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#=== FLASK ENDPOINT ===

@app.route(f"/{BOT_TOKEN}", methods=["POST"]) def receive_update(): update = Update.de_json(request.get_json(force=True), bot_app.bot) asyncio.run(bot_app.process_update(update)) return "OK"

@app.route("/") def index(): return "🤖 Dexmate AI is Running!"

#=== SET WEBHOOK ===

async def set_webhook(): bot = Bot(token=BOT_TOKEN) await bot.set_webhook(BASE_URL) logger.info("✅ Webhook set. Bot is ready!")

if name == 'main': loop = asyncio.get_event_loop() loop.run_until_complete(set_webhook()) logger.info("✅ Bot is Live on Render!") app.run(host="0.0.0.0", port=10000)

