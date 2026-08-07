import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

@dataclass
class Context:
    semaphore: asyncio.Semaphore
    pool: ProcessPoolExecutor