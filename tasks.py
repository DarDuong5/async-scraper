from celery_app import app
from handlers import handle_scrape, parse_html
import asyncio
import httpx
from sqlalchemy.orm import Session

from job import Status
from database import JobTable, engine

async def fetch_one(job_id: int,
                    url: str, 
                    client: httpx.AsyncClient, 
                    semaphore: asyncio.Semaphore):
    try:
        html_text = await handle_scrape(url, client, semaphore)
        return job_id, html_text, None
    except Exception as e:
        return job_id, None, e

async def fetch_many(urls: list[tuple[int, str]]):
    semaphore = asyncio.Semaphore(10)
    async with httpx.AsyncClient(timeout=3.1, follow_redirects=True) as client:
        coros = [asyncio.create_task(fetch_one(job_id, url, client, semaphore))
                      for job_id, url in urls]
        for coro in asyncio.as_completed(coros):
            id, value, error = await coro
            if error is not None:
                with Session(engine) as session:
                    job_row = session.get(JobTable, id)
                    job_row.status = Status.FAILED
                    job_row.value = value
                    job_row.error = str(error)
                    session.commit()
                continue    
            parse.delay(id, value)

@app.task(queue='fetch')
def fetch(urls: list[tuple[int, str]]):
    for job_id, _ in urls:
        with Session(engine) as session:
            job_row = session.get(JobTable, job_id)
            if job_row is None:
                raise ValueError(f'Job row does not exist given {job_id}.')
            job_row.status = Status.RUNNING
            session.commit()

    asyncio.run(fetch_many(urls))

@app.task(queue='parse')
def parse(job_id: int, html_text: str):
    try:
        result = parse_html(html_text)
        status, value, error = Status.DONE, result, None
    except Exception as e:
        status, value, error = Status.FAILED, None, str(e)

    with Session(engine) as session:
        job_row = session.get(JobTable, job_id)
        if job_row is None:
            raise ValueError(f'Job row does not exist given {job_id}.')
        job_row.status = status
        job_row.value = value
        job_row.error = error
        session.commit()