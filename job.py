from enum import StrEnum
from dataclasses import dataclass, field
from typing import Mapping, NamedTuple, Any
from itertools import count
import random

_id_counter = count(1)
def generate_id() -> int:
    return next(_id_counter)

class Status(StrEnum):
    PENDING = 'pending'
    RUNNING = 'running'
    DONE = 'done'
    FAILED = 'failed'

@dataclass
class Job:
    job_type: str
    status: Status
    id: int = field(default_factory=generate_id)
    payload: Mapping = field(default_factory=dict)  

class JobResult(NamedTuple):
    id: int
    status: Status
    value: Any | None = None
    error: str | None = None
