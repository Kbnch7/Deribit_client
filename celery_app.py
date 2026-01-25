# celery_app.py
from celery import Celery
from celery.schedules import crontab
from app.config import CELERY_BROKER_URL  # Assuming CELERY_BROKER_URL is defined in config.py, e.g., "redis://localhost:6379/0"

celery = Celery(
    'deribit_client_api',  # Replace with your project_name
    broker=CELERY_BROKER_URL,
    include=['app.tasks.celery_tasks']
)

celery.conf.beat_schedule = {
    'fetch-prices-every-minute': {
        'task': 'app.tasks.celery_tasks.fetch_and_save_prices',
        'schedule': 60,
    }
}