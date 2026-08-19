from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from job import Status
from database import get_session, JobTable
from tasks import fetch

app = FastAPI()

class JobBase(BaseModel):
    id: int
    status: Status
    url: str

@app.post('/jobs', response_model=list[JobBase])
async def upload_job(urls: list[str], session: Session = Depends(get_session)):
    rows = [JobTable(status=Status.PENDING, url=url) for url in urls]
    session.add_all(rows)
    session.commit()

    for row in rows:
        fetch.delay(row.id, row.url)

    return rows

@app.get('/jobs/{id}')
def fetch_job(id: int, session: Session = Depends(get_session)):
    job_row = session.get(JobTable, id)
    if job_row is None:
        return {'Error': 'Given ID does not exist.'}
    return {'status': job_row.status, 'value': job_row.value, 'error': job_row.error}

