# Async Scraper

Async Scraper is a concurrent scraper built on a job queue. It fetches URLs asynchronously with bounded concurrency via semaphore, and parses HTML per web page in a separate process. This enables I/O-bound fetching and CPU-bound parsing to run on the concurrency model suited for them. 

## Overview

Async Scraper separates *what work is done* and *how it's scheduled*. Jobs are submitted to a queue where a pool of workers takes them and dispatches each to a handler looked up in a registry, so adding a new job type means writing one decorated function without changing anything in the engine. The scraper itself is one handler, which fetches a web page and passes the HTML parsing to a process pool, keeping the event loop free to handle other fetches. 

## Features
- **Pluggable Job Types** - There may be unrelated job types, so we can use a decorator on any new function without changing the engine.
- **Hybrid concurrency** - Fetching URLs is I/O-bound handled by coroutines, and parsing HTML is CPU-bound handled by a process pool.
- **Bounded concurrency** - Limits the number of coroutines that can be executed concurrently at a time, without flooding the server.
- **Error isolation** - When a job fails, it gets recorded without crashing the program, allowing the worker to still run as well as the others.
- **Graceful shutdown** - Using sentinels tells a worker that there's no more work to do, so it stops cleanly.

## Architecture
[TODO]

## Setup
Requires Python 3.11+.
```
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage
Run:
```
python3 main.py
```

Sample Output:
```
ID: 1 | Status: done | Value: {'A Light in the Attic': '£51.77', 'Tipping the Velvet': '£53.74', ...}
ID: 6 | Status: failed | Value: None | Error: Client error '404 Not Found' ...
...
Successes: 5
Failures: 4
Elapsed: 0.3952s
```

## Project structure
Relevant files:
```
context.py # Defines Context with the shared resources semaphore, process pool, and HTTP client passed to handlers.
handlers.py # Any new and existing job handlers goes here.
job.py # Job and JobResult defined here.
main.py # Entry point that runs the program.
runner.py # The engine -- worker pool, job queue, dispatch loop, and result collection.
registry.py # @register decorator and job handler dispatch table.
handlers.py # Any new and existing job handlers goes here.
context.py # The Context bundling semaphore, process pool, and HTTP client to get passed to handlers.
job.py # Job and JobResult defined here.
samples.py # Example jobs for putting into the queue.
```

## Roadmap
- Stage 1: In-memory - DONE
- Stage 2: FastAPI and SQLAlchemy - IN-PROGRESS
- Stage 3: Redis, Docker, and AWS - NOT YET STARTED 

## License
MIT.