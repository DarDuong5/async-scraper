import asyncio
from typing import Mapping
import bs4 

from context import Context
from registry import register

def parse_html(html: str) -> Mapping:
    soup = bs4.BeautifulSoup(html, 'html.parser')
    book_to_price = {}
    for pod in soup.select('article.product_pod'):
        title = pod.select_one('h3 a')['title']
        price = pod.select_one('p.price_color').text.strip()
        book_to_price[title] = price
    return book_to_price 
    
@register('scrape')
async def handle_scrape(payload: Mapping, context: Context) -> Mapping:
    url = payload['url']
    async with context.semaphore:
        resp = await context.client.get(url)
        resp.raise_for_status()
        html = resp.text
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(context.pool, parse_html, html)
