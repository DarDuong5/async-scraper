import celery

app = celery.Celery('tasks', 
                    broker='redis://localhost:6379/0', 
                    include=['tasks']
                    )

app.conf.task_default_queue = 'fetch'