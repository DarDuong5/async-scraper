import asyncio
from typing import Mapping

from context import Context
from registry_handler import register

def factorial(n: int) -> int: # not recursive due to Python's recursion max depth limit :P
    res = 1
    for i in range(n, 1, -1):
        res *= i
    return len(str(res))

@register('scrape')
async def handle_scrape(payload: Mapping, context: Context) -> str:
    url = payload['url']
    delay = payload['delay']
    async with context.semaphore:
        await asyncio.sleep(delay)
        return f'Fetched {url}'

@register('process')
async def handle_process(payload: Mapping, context: Context) -> int:
    n = payload['n']
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(context.pool, factorial, n)
