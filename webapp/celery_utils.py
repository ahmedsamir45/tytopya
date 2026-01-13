from celery import Celery, Task
from flask import Flask

class FlaskTask(Task):
    def __call__(self, *args: object, **kwargs: object) -> object:
        with self.app.flask_app.app_context():
            return self.run(*args, **kwargs)

def celery_init_app(app: Flask) -> Celery:
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.flask_app = app
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
