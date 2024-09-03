# app/celery_worker.py

from celery import Celery
from flask import Flask

def make_celery(app: Flask) -> Celery:
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def init_celery():
    from app import create_app
    app = create_app()
    return make_celery(app)

celery = init_celery()
