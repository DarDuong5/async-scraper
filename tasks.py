from celery_app import app
from handlers import handle_scrape
from typing import Mapping
import asyncio
import httpx
from sqlalchemy.orm import Session

from job import Status
from database import JobTable, engine

@app.task
def work(job_id: int, payload: Mapping):
    with Session(engine) as session:
        job_row = session.get(JobTable, job_id)
        if job_row is None:
            raise ValueError(f'Job row does not exist given {job_id}.')
        job_row.status = Status.RUNNING
        session.commit()

    async def run():
        async with httpx.AsyncClient(timeout=3.1, follow_redirects=True) as client:
            return await handle_scrape(payload, client)

    try:
        result = asyncio.run(run())
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
