import logging

from telegram.ext import ApplicationBuilder, CommandHandler

from config import settings
from handlers import ai_news, start

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    app = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ai_news", ai_news))
    app.run_polling()
