# AI News Telegram Bot

This project is a Telegram bot that fetches, classifies, and summarizes top stories from Hacker News related to AI, ML, Data Science, and related fields.

## Features

- Fetches top stories from Hacker News.
- Uses NLP to summarize articles.
- Classifies stories into relevant AI/ML/DS categories.
- Telegram commands:
  - `/start` — Welcome message.
  - `/ai_news` — Get summarized and categorized AI news.

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Copy `.env.example` to `.env` and set your `TELEGRAM_TOKEN`.


4. **Run the bot:**
   ```bash
   python bot.py
   ```

## Project Structure

- `bot.py` — Entry point, sets up Telegram command handlers.
- `handlers.py` — Command handler functions.
- `services/` — Contains `hackernews.py` and `nlp.py` for external API logic.
- `config.py` — Loads settings.

## License

MIT