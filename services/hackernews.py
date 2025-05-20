import asyncio

import aiohttp

from config import settings

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


class HackerNewsService:
    @staticmethod
    async def fetch_top_stories(limit: int | None = None) -> list[int]:
        limit = limit or settings.HN_TOP_LIMIT
        async with aiohttp.ClientSession() as session:
            async with session.get(
                TOP_STORIES_URL, params={"print": "pretty"}, timeout=5
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data[:limit]

    @staticmethod
    async def fetch_item(item_id: int) -> dict:
        url = ITEM_URL.format(id=item_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"print": "pretty"}, timeout=5) as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    async def fetch_items_parallel(
        item_ids: list[int], max_concurrent: int = 5
    ) -> list[dict]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(item_id):
            async with semaphore:
                return await HackerNewsService.fetch_item(item_id)

        tasks = [fetch_with_semaphore(item_id) for item_id in item_ids]
        for coro in asyncio.as_completed(tasks):
            result = await coro
            yield result


def main():
    """Main function to run the fetcher."""

    async def run():
        hn_service = HackerNewsService()
        stories = await hn_service.fetch_top_stories()
        items = hn_service.fetch_items_parallel(stories, max_concurrent=5)
        async for story in items:
            print(f"{story.get('title', 'No Title')} ({story.get('url', 'No URL')})")

    asyncio.run(run())


if __name__ == "__main__":
    main()
