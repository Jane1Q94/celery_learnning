from celery import Celery


class MyCelery(Celery):

    def gen_task_name(self, name, module):
        task_name = super().gen_task_name(name, module)
        return f'1q94-{task_name}'


app = MyCelery("app", broker="redis://localhost",
               backend="redis://localhost", include=["userguide.task.tasks"])
