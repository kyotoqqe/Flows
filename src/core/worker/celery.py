from celery import Celery

from src.core.worker.config import celery_settings

app = Celery(__name__)

settings_dict = celery_settings.model_dump()
print(settings_dict)
app.conf.update(
    **settings_dict
)
app.autodiscover_tasks(["src.core.worker"])


