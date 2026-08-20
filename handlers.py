from typing import Mapping
import bs4 
from asyncio import Semaphore
from httpx import AsyncClient

def parse_html(html: str) -> Mapping:
    soup = bs4.BeautifulSoup(html, 'html.parser')
    book_to_price = {}
    for pod in soup.select('article.product_pod'):
        title = pod.select_one('h3 a')['title']
        price = pod.select_one('p.price_color').text.strip()
        book_to_price[title] = price
    return book_to_price 
    
async def handle_scrape(url: str, client: AsyncClient, semaphore: Semaphore) -> str:
    async with semaphore:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text
