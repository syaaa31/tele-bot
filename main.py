import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# 🔑 Load secrets from Render Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("❌ Missing BOT_TOKEN or GROQ_API_KEY. Set them in Render Dashboard.")

# 🤖 Groq client
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# 📄 Load your notes (from notes.txt in repo)
with open("notes.txt", "r", encoding="utf-8") as f:
    notes_text = f.read()

# 🧠 Function to ask AI
def ask_question(question: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful digital trainer. Use the following notes to answer student questions."},
        {"role": "user", "content": f"Notes:\n{notes_text}\n\nQuestion: {question}"}
    ]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content

# 👋 /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Haii everyone!👋\nI'm your hybrid digital electronic trainer AI chatbot🤖\n\n"
        "You can ask me anything based on our module. Just type your question below!"
    )

# 💬 Handle user questions
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text

    # Typing animation
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await asyncio.sleep(1.5)

    # Get AI answer
    answer = ask_question(user_question)
    await update.message.reply_text(answer)

# 🚀 Bot runner
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
