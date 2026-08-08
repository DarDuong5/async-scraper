from typing import Callable, TypeVar, TypeAlias, Mapping, Any, Awaitable
from context import Context

Handler: TypeAlias = Callable[[Mapping, Context], Awaitable[Any]]
JOB_HANDLERS: dict[str, Handler] = {}

C = TypeVar('C', bound=Callable)

def register(job_type: str) -> Callable[[C], C]:
    def decorator(func: C) -> C:
        JOB_HANDLERS[job_type] = func
        return func
    return decorator

