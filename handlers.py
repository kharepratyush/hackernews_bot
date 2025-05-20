import logging
import time

from telegram import Update
from telegram.ext import ContextTypes

from services.hackernews import HackerNewsService
from services.nlp import NLPService

logger = logging.getLogger(__name__)

hn_service = HackerNewsService()
nlp_service = NLPService()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Use /ai_news to fetch Hacker News stories."
    )


async def ai_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text("Processing top Hacker News stories...")
    found = False

    stories = await hn_service.fetch_top_stories()
    items = hn_service.fetch_items_parallel(stories, max_concurrent=5)
    async for story in items:
        try:
            time.sleep(5)
            # print(f"{story.get('title', 'No Title')} ({story.get('url', 'No URL')})")
            title = story.get("title")
            url = story.get("url")
            if not (title and url):
                continue
            summary = await nlp_service.summarize_article(url)
            category = await nlp_service.classify_topic(
                (title + "\n" + summary).strip()
            )
            if category not in [
                "Machine Learning",
                "Artificial Intelligence",
                "Deep Learning",
                "Reinforcement Learning",
                "Natural Language Processing",
                "Computer Vision",
                "Data Science",
                "Statistics",
                "AI Agents & Tools",
                "Embeddings"
            ]:
                # print(title, summary, category)
                continue

            print(title, summary, category)

            summary = await nlp_service.summarize_article(url)
            msg = f"*[{category}]* {title}\n{url}\n{summary}"
            await update.message.reply_markdown(msg)
            found = True
        except Exception as e:
            logger.error("Error processing story: %s", e)

    if not found:
        await update.message.reply_text(
            "No relevant AI/ML/DS/statistics stories found."
        )
