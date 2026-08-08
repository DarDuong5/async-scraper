import asyncio
from typing import Mapping
import httpx


from context import Context
from registry_handler import register

def factorial(n: int) -> int: # not recursive due to Python's recursion max depth limit :P
    res = 1
    for i in range(n, 1, -1):
        res *= i
    return len(str(res))

@register('scrape')
async def handle_scrape(payload: Mapping, context: Context) -> int:
    url = payload['url']
    async with context.semaphore:
        resp = await context.client.get(url)
        resp.raise_for_status()
        return len(resp.text)
        
@register('process')
async def handle_process(payload: Mapping, context: Context) -> int:
    n = payload['n']
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(context.pool, factorial, n)
