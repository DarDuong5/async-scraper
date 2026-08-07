import asyncio
from concurrent import futures
from typing import TypeAlias
import time
import sys
import tqdm

from context import Context
from job import Job, JobResult, Status
from registry_handler import JOB_HANDLERS
import handlers # imported because the register decorators needs to be ran, iykyk
from samples import SAMPLE_JOBS

sys.set_int_max_str_digits(0) # 0 disables the limit

JobQueue: TypeAlias = asyncio.Queue[Job]
ResultQueue: TypeAlias = asyncio.Queue[JobResult]

async def worker(jobs: JobQueue, 
                 results: ResultQueue, 
                 context: Context) -> None:
    while True:
        job = await jobs.get()
        if job is None:
            break
        try:
            value = await JOB_HANDLERS[job.job_type](job.payload, context)
            results.put_nowait(JobResult(job.id, Status.DONE, value=value))
        except Exception as e:
            results.put_nowait(JobResult(job.id, Status.FAILED, error=str(e)))
    results.put_nowait(JobResult(None, None, None, None))

def enqueue_jobs(jobs: JobQueue) -> None:
    for j in SAMPLE_JOBS:
        job = Job(j['job_type'], Status.PENDING, payload=j['payload'])
        jobs.put_nowait(job)

def enqueue_sentinels(n_workers: int, jobs: JobQueue) -> None:
    for _ in range(n_workers):
        jobs.put_nowait(None)

async def main() -> None:
    start = time.perf_counter()
    jobs: JobQueue = asyncio.Queue()
    results: ResultQueue = asyncio.Queue()
    num_workers = 5
    with futures.ProcessPoolExecutor() as pool:
        semaphore = asyncio.Semaphore(10)
        context: Context = Context(semaphore, pool)
        enqueue_jobs(jobs)
        enqueue_sentinels(num_workers, jobs)
        tasks = [asyncio.create_task(worker(jobs, results, context))
                 for _ in range(num_workers)]
        await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start
    report(num_workers, results, elapsed)

def report(n_workers: int, results: ResultQueue, elapsed: float) -> None:
    successes, failures = [], []
    checked, workers_done = 0, 0
    while workers_done < n_workers:
        id, status, value, error = results.get_nowait()
        if id is None:
            workers_done += 1
        else:
            if status == Status.DONE:
                successes.append((id, value))
            else:
                failures.append((id, error))
            checked += 1
            print(f'ID: {id:>4} | Status: {status:>10} | Value: {value!s:>24} | Error: {error}')
    print(f'Checked: {checked}')
    print(f'Successes: {len(successes)}')
    print(f'Failures: {len(failures)}')
    print(f'Elapsed: {elapsed:.4f}s')
