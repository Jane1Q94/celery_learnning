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
