from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio
from concurrent import futures
import httpx

from job import Job, Status
from runner import worker
from context import Context

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the context first once started
    app.state.job_queue = asyncio.Queue()
    app.state.result_queue = asyncio.Queue()
    num_workers = 5
    num_semaphore = 10
    with futures.ProcessPoolExecutor() as pool:
        async with httpx.AsyncClient(timeout=3.1, follow_redirects=True) as client:
            semaphore = asyncio.Semaphore(num_semaphore)
            app.state.context = Context(semaphore, pool, client)
            # Then spawn the workers
            workers = [asyncio.create_task(worker(app.state.job_queue, 
                                                  app.state.result_queue, 
                                                  app.state.context))
                       for _ in range(num_workers)]
            yield # App runs
            # Cancel the workers after shutdown
            for w in workers:
                w.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
        # Release the resources after workers are cancelled here

app = FastAPI(lifespan=lifespan)

class JobBase(BaseModel):
    job_type: str
    payload: dict

@app.post('/jobs')
def upload_job(job_base: JobBase, request: Request):
    job = Job(job_base.job_type, Status.PENDING, payload=job_base.payload)
    request.app.state.job_queue.put_nowait(job)
    return {'id': job.id, 'job_type': job.job_type, 'status': job.status, 'payload': job.payload}

@app.get('/jobs/{id}')
def fetch_job(id: int):
    ...