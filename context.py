import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import httpx

@dataclass
class Context:
    semaphore: asyncio.Semaphore
    pool: ProcessPoolExecutor
    client: httpx.AsyncClient