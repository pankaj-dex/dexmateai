import os
import logging
from flask import Flask, request, Response
import openai  # OpenAI Python SDK
from telegram import Update
from telegram.ext import (
    Application, MessageHandler, filters, ContextTypes
)

# 1. Configuration
# Load environment variables or use defaults.
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN", "7866890680:AAFfFtyIv4W_8_9FohReYvRP7wt9IbIJDMA")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://<your-domain-or-ngrok>/webhook")

# 2. Logging configuration for diagnostics3
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 3. Initialize Flask app for webhook
app = Flask(__name__)

# 4. Initialize OpenAI client (or set up alternative LLM here)
openai.api_key = OPENAI_API_KEY

# 5. Create the Telegram Application (async) and add handlers
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all user messages: send greeting and AI response."""
    user_text = update.message.text or ""
    # Friendly greeting message
    greeting = "How are you? Do you need any help? How can I help you?"
    try:
        # Query the AI model (here GPT-3.5). Replace with free model logic if needed.
        response = await get_ai_response(user_text)
    except Exception as e:
        logger.error("AI response failed: %s", e)
        response = "Sorry, I couldn't generate a response at this time."
    # Combine greeting and AI answer
    reply_text = f"{greeting}\n\n{response}"
    await update.message.reply_text(reply_text)

async def get_ai_response(prompt: str) -> str:
    """
    Get a response from the AI model. 
    Currently uses OpenAI ChatCompletion (GPT-3.5)4; replace or modify for other models.
    """
    if not prompt:
        return "Tell me something so I can help you!"
    completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return completion.choices[0].message.content.strip()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify the user."""
    logger.error("Update caused error: %s", context.error)
    # Optionally notify user about the error (if update has a chat)
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An unexpected error occurred. Please try again later."
            )
        except Exception as e:
            logger.error("Failed to send error message: %s", e)

# Register the message handler for all text (non-command) messages5
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
application.add_error_handler(error_handler)

# 6. Define Flask route for Telegram webhook
@app.route("/webhook", methods=["POST"])
async def webhook() -> Response:
    """
    Endpoint for Telegram to send updates. We convert the POSTed JSON into an Update object
    and let the Application process it6.
    """
    try:
        data = await request.get_json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error("Failed to process update: %s", e)
        return Response(status=400)
    return Response(status=200)

# 7. Initialize the bot and set webhook (done once at startup)
def setup_bot():
    """
    Initialize application (required for manual update processing) and set the webhook URL.
    """
    # Initialize the Application (this must be done before processing updates)
    import asyncio
    asyncio.get_event_loop().run_until_complete(application.initialize())
    # Set the Telegram webhook to our /webhook URL
    webhook_success = application.bot.set_webhook(url=WEBHOOK_URL)
    if webhook_success:
        logger.info("Webhook set to %s", WEBHOOK_URL)
    else:
        logger.error("Failed to set webhook!")

# 8. Run the Flask app (for local testing)
if __name__ == "__main__":
    setup_bot()
    port = int(os.environ.get("PORT", "5000"))
    logger.info("Starting Flask server on port %s...", port)
    app.run(host="0.0.0.0", port=port)