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
