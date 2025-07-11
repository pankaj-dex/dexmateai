#Main.py

import os import logging import asyncio from flask import Flask, request from telegram import Update, Bot, constants from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters import openai import httpx import base64

#Set up logging

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

#Load environment variables (API keys)

BOT_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA" OPENROUTER_API_KEY = "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"

#Flask app for webhook

app = Flask(name)

#Telegram Bot setup

bot_app = ApplicationBuilder().token(BOT_TOKEN).build() bot = Bot(BOT_TOKEN)

#AI reply function using OpenRouter API

async def get_ai_reply(prompt): try: headers = { "Authorization": f"Bearer {OPENROUTER_API_KEY}", "HTTP-Referer": "https://dexmateai.onrender.com", "Content-Type": "application/json", } json = { "model": "openrouter/openchat-3.5", "messages": [ {"role": "system", "content": "You are a helpful AI assistant who helps users with coding and general queries."}, {"role": "user", "content": prompt} ] } async with httpx.AsyncClient() as client: res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=json) data = res.json() return data["choices"][0]["message"]["content"] except Exception as e: logger.error(f"AI Error: {e}") return "Sorry, something went wrong while getting a response."

#Save chat logs

def save_chat_log(user_id, message): with open(f"chat_logs/{user_id}.txt", "a", encoding="utf-8") as f: f.write(message + "\n")

#Message handler

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): user_message = update.message.text or "" user_id = update.message.from_user.id message = user_message.strip().lower()

if message:
    save_chat_log(user_id, f"User: {user_message}")
    if message in ["hi", "hello", "hey"]:
        reply = "How are you? Do you need any help? How can I help you?"
    else:
        reply = await get_ai_reply(user_message)
    await update.message.reply_text(reply)
    save_chat_log(user_id, f"Bot: {reply}")

#Photo/doc upload

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("📷 Thanks for the photo! How can I help you with it?")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("📄 Thanks for the document! I'll check if I can help with it.")

#Voice message

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("🎤 Thanks for your voice message! Voice-to-text is coming soon.")

#Add handlers

bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) bot_app.add_handler(MessageHandler(filters.PHOTO, handle_photo)) bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_document)) bot_app.add_handler(MessageHandler(filters.VOICE, handle_voice))

#Flask webhook route

@app.route(f"/{BOT_TOKEN}", methods=["POST"]) def webhook(): update = Update.de_json(request.get_json(force=True), bot) asyncio.run(bot_app.process_update(update)) return "OK"

#Home route for Render health check

@app.route("/") def index(): return "Dexmate AI is live!"

if name == "main": os.makedirs("chat_logs", exist_ok=True) logger.info("\u2705 Bot is Live on Render!") bot_app.initialize() bot_app.run_polling()  # for local test, not needed on Render app.run(host="0.0.0.0", port=10000)

