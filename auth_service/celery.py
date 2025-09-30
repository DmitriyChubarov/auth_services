import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')

app = Celery('auth_service', broker=f'redis://{os.environ.get("REDIS_HOST")}:6379/0')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
