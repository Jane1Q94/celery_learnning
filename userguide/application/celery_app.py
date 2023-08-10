from celery import Celery, Task


class MyCelery(Celery):

    def gen_task_name(self, name, module):
        task_name = super().gen_task_name(name, module)
        return f'1q94-{task_name}'


class BaseTask(Task):
    def __init__(self) -> None:
        print("start init")

    @property
    def payload(self):
        return {
            "db_connection": "this is a db connection"
        }


app = MyCelery("app", broker="redis://localhost",
               backend="redis://localhost", include=["userguide.task.tasks"],
               task_cls="userguide.application.celery_app:BaseTask")
