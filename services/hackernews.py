import asyncio
import aiosqlite
import aiohttp

from config import settings

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
BEST_STORIES_URL = "https://hacker-news.firebaseio.com/v0/beststories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

class HackerNewsService:

    @staticmethod
    async def fetch_top_stories(limit: int | None = None) -> list[int]:
        limit = limit or settings.HN_TOP_LIMIT
        top_stories = await HackerNewsService._get_top_story_ids()
        best_stories = await HackerNewsService._get_best_story_ids()
        data = list(set(top_stories + best_stories))
        new_ids = await HackerNewsService._filter_and_cache_new_ids(data, limit)
        return new_ids

    @staticmethod
    async def _get_top_story_ids() -> list[int]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    TOP_STORIES_URL, params={"print": "pretty"}, timeout=5
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    async def _get_best_story_ids() -> list[int]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    BEST_STORIES_URL, params={"print": "pretty"}, timeout=5
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    async def _filter_and_cache_new_ids(data: list[int], limit: int) -> list[int]:
        async with aiosqlite.connect("hn_cache.db") as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY)"
            )
            cached = set()
            async with db.execute("SELECT id FROM stories") as cursor:
                async for row in cursor:
                    cached.add(row[0])
            new_ids = [story_id for story_id in data if story_id not in cached][:limit]
            if new_ids:
                await db.executemany(
                    "INSERT OR IGNORE INTO stories (id) VALUES (?)",
                    [(story_id,) for story_id in new_ids],
                )
                await db.commit()
        return new_ids

    @staticmethod
    async def fetch_item(item_id: int) -> dict:
        url = ITEM_URL.format(id=item_id)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params={"print": "pretty"}, timeout=5) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except aiohttp.ClientError as e:
            # Log or handle the exception as needed
            return {"error": f"Client error: {e}", "id": item_id}
        except asyncio.TimeoutError:
            return {"error": "Request timed out", "id": item_id}
        except Exception as e:
            return {"error": f"Unexpected error: {e}", "id": item_id}

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
            await asyncio.sleep(0.5)  # Rate limit: 1 request per second
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
