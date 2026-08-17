from enum import StrEnum
from dataclasses import dataclass, field
from typing import Mapping

class Status(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    DONE = 'done'
    FAILED = 'failed'

@dataclass
class Job:
    job_type: str
    status: Status
    id: int
    payload: Mapping = field(default_factory=dict)  

