from celery import Celery

from src.core.worker.config import celery_settings

app = Celery(__name__)

settings_dict = celery_settings.model_dump()
print(settings_dict)
app.conf.update(
    **settings_dict
)
app.autodiscover_tasks(["src.core.worker"])
app.conf.task_routes = {
    "mailing.tasks.*" : {"queue": "mailing"}
}

def get_route_tasks():
    from src.core.worker.tasks import send_email

    ROUTE_TASK = {
        "send_email": send_email,
    }
    return ROUTE_TASK