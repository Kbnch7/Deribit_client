# celery_app.py
from celery import Celery
from celery.schedules import crontab
from app.config import CELERY_BROKER_URL

celery = Celery(
    'deribit_client_api',
    broker=CELERY_BROKER_URL,
    include=['app.tasks.celery_tasks']
)

celery.conf.beat_schedule = {
    'fetch-prices-every-minute': {
        'task': 'app.tasks.celery_tasks.fetch_and_save_prices',
        'schedule': 3,
    }
}
