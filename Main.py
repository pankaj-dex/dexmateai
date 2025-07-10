from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os, wave, json, atexit

# (Optional) Vosk for offline ASR
try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    Model = None

# Initialize Telegram Bot (set your BOT_TOKEN environment variable)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Initialize Vosk model if available
if Model:
    vosk_model = Model(lang="en-us")  # path to model directory or 'en-us'
    rec = KaldiRecognizer(vosk_model, 16000)
else:
    rec = None

# In-memory chat logs: {chat_id: [messages]}
chat_history = {}

# /start command
def start(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, "Hello! Send me a text, photo, or voice. I'm here to help with your coding questions.")

# Handle incoming text messages
def handle_text(update, context):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    chat_history.setdefault(chat_id, []).append({"role": "user", "text": user_text})
    # TODO: Call LLM or code model here to generate a response
    # For now, just echo back:
    bot_response = f"You said: {user_text}"
    chat_history[chat_id].append({"role": "bot", "text": bot_response})
    context.bot.send_message(chat_id, bot_response)

# Handle incoming photos
def handle_photo(update, context):
    chat_id = update.effective_chat.id
    photo = update.message.photo[-1]
    file_id = photo.file_id
    new_file = context.bot.get_file(file_id)
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{file_id}.jpg"
    new_file.download(file_path)
    chat_history.setdefault(chat_id, []).append({"role": "user", "text": f"<Photo saved at {file_path}>"})
    context.bot.send_message(chat_id, "Photo received and saved. Thanks!")

# Handle incoming voice messages (transcribe with Vosk)
def handle_voice(update, context):
    chat_id = update.effective_chat.id
    voice = update.message.voice
    file_id = voice.file_id
    new_file = context.bot.get_file(file_id)
    os.makedirs("downloads", exist_ok=True)
    ogg_path = f"downloads/{file_id}.oga"
    new_file.download(ogg_path)
    # Convert OGG to WAV for Vosk
    wav_path = ogg_path.replace(".oga", ".wav")
    os.system(f"ffmpeg -y -i {ogg_path} -ar 16000 -ac 1 {wav_path}")
    if rec:
        wf = wave.open(wav_path, "rb")
        rec.AcceptWaveform(wf.readframes(wf.getnframes()))
        result = json.loads(rec.FinalResult())
        text = result.get("text", "")
    else:
        text = "<transcription disabled>"
    chat_history.setdefault(chat_id, []).append({"role": "user", "text": text})
    context.bot.send_message(chat_id, f"You (via voice): {text}")

# Save chat history to a file on exit
def save_logs():
    with open("chat_logs.json", "w") as f:
        json.dump(chat_history, f, indent=2)

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice))
atexit.register(save_logs)

# Start the bot
if __name__ == '__main__':
    updater.start_polling()
    updater.idle()