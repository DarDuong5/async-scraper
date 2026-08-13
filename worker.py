import asyncio
from typing import TypeAlias
from sqlalchemy.orm import Session

from context import Context
from job import Job, Status
from registry import JOB_HANDLERS
import handlers # imported because the register decorators needs to be ran, iykyk
from database import engine, JobTable

JobQueue: TypeAlias = asyncio.Queue[Job]

async def worker(jobs: JobQueue, context: Context) -> None:
    while True:
        job = await jobs.get()
        try:
            value = await JOB_HANDLERS[job.job_type](job.payload, context)
            status, val, error = Status.DONE, value, None
        except Exception as e:
            status, val, error = Status.FAILED, None, str(e)
        with Session(engine) as session:
            job_row = session.get(JobTable, job.id)
            if job_row is None:
                continue
            job_row.status = status
            job_row.value = val
            job_row.error = error
            session.commit()
