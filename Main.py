✅ Dexmate AI Bot (Production-Ready, Feature-Rich, Free & Scalable)

➤ FILE: Main.py

import os import logging import openai import asyncio from flask import Flask, request from telegram import Update, Bot from telegram.ext import ( ApplicationBuilder, MessageHandler, ContextTypes, filters ) import httpx

=== CONFIG ===

TELEGRAM_TOKEN = "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA" OPENROUTER_API_KEY = "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" BASE_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

=== LOGGING ===

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

=== FLASK APP ===

app = Flask(name)

=== TELEGRAM APP ===

bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).

