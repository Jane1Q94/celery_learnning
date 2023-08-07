
### task message ack
a task message is not removed from the queue until that message has been acknowledged by a worker. 
Since the worker cannot detect if your tasks are idempotent(幂等), the default behavior is to acknowledge the message in advance, just before it’s executed, so that a task invocation that already started is never executed again.


### task multi decorators
```python
@app.task
@decorator2
@decorator3
def tasksample():
    pass
```

### bound tasks
a task being bound means the first arguments to the task will alwasys be the task instance(self).
`app.Task.retry()` need bound tasks for accessing information about the current task request.
```python
@app.task(bind=True)
def add(self, x, y):
    print(f'requestid: {self.request.id}')
```

### logger
A special logger named 'celery.task', you can inherit from this logger to auto matically get the task name and unique id as part of the logs.
!["logger"](./screenshots/logger.png)
```python
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
```

### retry
default retry will happen in 180s
you can override this setting by specify the `default_retry_delay` parameter to `@app.task()` or using `countdown` parameter in `self.retry`
![retry](./screenshots/retry.png)
default retry count is 3, see below:
![retry count](./screenshots/retry2.png)

 ### parametes
 - acks_late: acknowledge the message after the task returns
 - bind
 - base: base class of the task
 - default_retry_delay: retry delay
 - autoretry_for: retry for a particular exception
 - retry_kwargs: retry parameters, eg: `{'max_retries': 5}`
 ![auto retry](./screenshots/retry3.png)
 - retry_backoff=True: use exponential backoff to avoid overwhelming the service

 ### settings
 - task_reject_on_worker_lost: you really want to be redelivered the messages if the child process is be killed by system or calling sys.exit()

### attention
- i/o tasks need add timeout because a task indefinitely may eventually stop the worker instance from doing any other work.
