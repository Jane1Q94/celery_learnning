"""Celery -A nextstep.celery_app -l INFO
"""

from celery import Celery

app = Celery('nextstep',
             broker="redis://localhost",
             backend="redis://localhost",
             include=['nextstep.tasks'])


app.conf.update(
    result_expires=3600
)

if __name__ == "__main__":
    app.start()
