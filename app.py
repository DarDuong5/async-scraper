from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio
from concurrent import futures
import httpx
from sqlalchemy.orm import Session

from job import Job, Status
from worker import worker
from context import Context
from database import get_session, engine, Base, JobTable
from tasks import work

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database
    Base.metadata.create_all(engine)
    # Create the context first once started
    app.state.job_queue = asyncio.Queue()
    num_workers = 5
    num_semaphore = 10
    with futures.ProcessPoolExecutor() as pool:
        async with httpx.AsyncClient(timeout=3.1, follow_redirects=True) as client:
            semaphore = asyncio.Semaphore(num_semaphore)
            app.state.context = Context(semaphore, pool, client)
            # Then spawn the workers
            workers = [asyncio.create_task(worker(app.state.job_queue, app.state.context))
                       for _ in range(num_workers)]
            yield # App runs
            # Cancel the workers after shutdown
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
        # Release the resources after workers are cancelled here

app = FastAPI()

class JobBase(BaseModel):
    job_type: str
    payload: dict

@app.post('/jobs')
async def upload_job(job_base: JobBase, 
               session: Session = Depends(get_session)):
    # Create a database row
    job_row = JobTable(job_type=job_base.job_type, status=Status.PENDING, payload=job_base.payload)
    session.add(job_row)
    session.commit()
    session.refresh(job_row)
    work.delay(job_row.id, job_row.payload)
    return {'id': job_row.id, 'job_type': job_row.job_type, 'status': job_row.status, 'payload': job_row.payload}

@app.get('/jobs/{id}')
def fetch_job(id: int, session: Session = Depends(get_session)):
    job_row = session.get(JobTable, id)
    if job_row is None:
        return {'Error': 'Given ID does not exist.'}
    return {'status': job_row.status, 'value': job_row.value, 'error': job_row.error}

