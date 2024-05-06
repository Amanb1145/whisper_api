import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whisper_api.settings')

app = Celery('audioprocessing')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
