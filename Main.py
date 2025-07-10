Main.py

import os import logging import asyncio from flask import Flask, request from telegram import Update, Bot from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters import openai

=== CONFIG ===

BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA" OPENAI_API_KEY = "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" WEBHOOK_URL = "https://dexmateai.onrender.com/" + BOT_TOKEN PORT = 10000

openai.api_key = OPENAI_API_KEY

=== LOGGING ===

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

=== TELEGRAM APP ===

bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

=== MESSAGE HANDLER ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_message = update.message.text.lower() if "hello" in user_message: await update.message.reply_text("How are you? Do you need any help? How can I help you?") else: try: response = openai.ChatCompletion.create( model="gpt-3.5-turbo", messages=[{"role": "user", "content": user_message}], temperature=0.7 ) bot_reply = response.choices[0].message.content await update.message.reply_text(bot_reply) except Exception as e: logger.error(f"Error from OpenAI: {e}") await update.message.reply_text("Sorry, something went wrong. Please try again later.")

bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

=== FLASK ===

app = Flask(name)

@app.route(f"/{BOT_TOKEN}", methods=["POST"]) def receive_update(): update = Update.de_json(request.get_json(force=True), bot_app.bot) asyncio.run(bot_app.initialize()) asyncio.run(bot_app.process_update(update)) return "OK"

@app.route("/") def home(): return "Dexmate AI Bot is Live!"

=== SET WEBHOOK AND RUN ===

async def set_webhook(): bot = Bot(BOT_TOKEN) await bot.set_webhook(WEBHOOK_URL) logger.info("✅ Webhook set. Bot is ready!")

if name == "main": asyncio.run(set_webhook()) logger.info("✅ Bot is Live on Render!") app.run(host="0.0.0.0", port=PORT)

