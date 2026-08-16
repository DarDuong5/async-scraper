from celery_app import app
from handlers import handle_scrape
import asyncio
import httpx

@app.task
def work(payload):
    async def run():
        async with httpx.AsyncClient(timeout=3.1, follow_redirects=True) as client:
            return await handle_scrape(payload, client)
    return asyncio.run(run())
