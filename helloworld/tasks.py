from celery import Celery

# The first argument to Celery is the name of the current module.
# This is only needed so that names can be automatically generated when the tasks are defined in the __main__ module.
app = Celery('tasks', backend='redis://localhost', broker='redis://localhost')

# app.conf.update(
#     task_serializer="json",
#     accept_content=["json"],
#     result_serializer="json",
#     timezone="Asia/Shanghai",
#     enable_utc=True,
# )

app.config_from_object('celeryconfig')


@app.task
def add(x, y):
    return x + y
