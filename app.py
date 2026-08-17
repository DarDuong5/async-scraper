from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from job import Status
from database import get_session, JobTable
from tasks import work

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

