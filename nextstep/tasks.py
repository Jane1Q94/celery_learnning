from nextstep.celery_app import app
from celery import Task


@app.task
def add(x, y) -> Task:
    return x + y


@app.task
def mul(x, y) -> Task:
    return x * y


@app.task
def xsum(numbers) -> Task:
    return sum(numbers)
