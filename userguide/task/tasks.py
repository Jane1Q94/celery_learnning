import time
from userguide.application.celery_app import app


@app.task
def create_user(username, password):
    print(f'username: {username}, password: {password}')


@app.task(bind=True)
def bind_create_user(self, username, password):
    print(f'username: {username}, password: {password}')
    print(f'id: {self.request.id} args: {self.request.args}')


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@app.task
def test_logger(x, y):
    logger.info(f'x: {x} y: {y}')
    return x + y


import sys


@app.task(bind=True)
def test_redirect_logger(self, x, y):
    old_outs = sys.stdout, sys.stderr
    rlevel = self.app.conf.worker_redirect_stdouts_level
    try:
        self.app.log.redirect_stdouts_to_logger(logger, rlevel)
        print(f'x: {x} y: {y}')
        return x + y
    finally:
        sys.stdout, sys.stderr = old_outs


@app.task(bind=True)
def test_retry(self):
    try:
        raise Exception("trigger exception manually")
    except Exception as exc:
        raise self.retry(exc=exc)


@app.task(bind=True, default_retry_delay=4)
def test_retry_delay(self):
    try:
        raise Exception("trigger exception manually")
    except Exception as exc:
        self.retry(exc=exc)


class CustomException(Exception):
    pass


@app.task(bind=True, autoretry_for=(CustomException, ), retry_kwargs={'max_retries': 5, 'countdown': 5})
def test_auto_retry(self):
    raise CustomException("custom exception")


@app.task(bind=True)
def test_custom_state(self, filenames):
    for i, file in enumerate(filenames):
        if not self.request.called_directly:
            self.update_state(state="PROGRESS", meta={
                'current': i,
                'current_file': file,
                'total': len(filenames)
            })
        time.sleep(4)
        logger.info(f'{self}')


class BadPickleCustomException(Exception):
    def __init__(self, status_code) -> None:
        self.status_code = status_code

# always in pending state


@app.task(serializer="pickle")
def test_bad_pickle_exception():
    raise BadPickleCustomException(400)


class NormalPickleCustomException(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super(NormalPickleCustomException, self).__init__(status_code)


@app.task(serializer="pickle")
def test_normal_pickle_exception():
    raise NormalPickleCustomException(400)


# custom base task class
from celery import Task


class DatabaseTask(Task):
    """every task instance can use the same db connection
    """
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = {
                "db": "this is a db connnection"
            }
        return self._db


@app.task(base=DatabaseTask, bind=True)
def test_task_base(self: Task):
    print(self.db)
    return self.db


@app.task(bind=True)
def test_global_task_base(self: Task):
    print(self.payload)
    return self.payload


# test task handlers

class BaseTaskHandlers(Task):
    # the return value of this handler is ignored.
    def before_start(self, task_id, args, kwargs):
        print(
            f'self: {self}, task_id: {task_id}, args: {args}, kwargs: {kwargs}')

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print(f'self: {self}, status: {status}: retval: {retval}, taskid: {task_id}, args: {args}, kwargs: {kwargs}, einfo: {einfo}')

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('task is failure')
        print(
            f'self: {self}, exc: {exc}, taskid: {task_id}, args: {args}, kwargs: {kwargs}, einfo: {einfo}')

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print('task is on retry')

    def on_success(self, retval, task_id, args, kwargs):
        print('task is success')


@app.task(base=BaseTaskHandlers, bind=True)
def test_task_handler_on_success(self):
    print('task execute success')
    return 'success'


# custom request
from celery.worker.request import Request


class CustomRequest(Request):
    def on_timeout(self, soft, timeout):
        super().on_timeout(soft, timeout)
        if not soft:
            logger.warning(
                f'A hard timeout was enforced for task {self.task.name}'
            )

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        super().on_failure(exc_info, send_failed_event, return_ok)
        logger.warning(f'Failure detected for task {self.task.name}')


class BasetaskCustomRequest(Task):
    Request = CustomRequest


@app.task(base=BasetaskCustomRequest, bind=True)
def test_custom_request(self):
    import requests
    requests.get("http://www.bai.com")


@app.task
def test_sync_call_children():
    print('parent task execute start')
    time.sleep(1)
    children_task.delay().get(disable_sync_subtasks=False)
    print('parent task execute done.')

# will failed:
# RuntimeError: Never call result.get() within a task!


@app.task
def test_async_call_children():
    print('parent task execute start')
    time.sleep(1)
    children_task.delay().get(disable_sync_subtasks=True)
    print('parent task execute done.')


@app.task
def children_task():
    print('children task execute start.')
    time.sleep(10)
    print('child task execute done')


@app.task
def test_link(x, y):
    return x + y


@app.task
def test_link_error(*args, **kwargs):
    print(f'args: {args}, kwargs: {kwargs}')


@app.task(bind=True)
def test_on_message(self, a, b):
    time.sleep(1)
    self.update_state(state="PROGRESS", meta={'progress': 50})
    time.sleep(1)
    self.update_state(state="PROGRESS", meta={'progress': 90})
    time.sleep(1)
    return f'success: {a} {b}'


def on_message(body):
    print(body)


@app.task(bind=True)
def test_retry_policy(self):
    time.sleep(1)
    raise CustomException("custom exception")
