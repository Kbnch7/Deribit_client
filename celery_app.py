from celery import Celery
from celery.schedules import crontab
from app.config import CELERY_BROKER_URL

celery = Celery(
    'deribit_client_api',
    broker=CELERY_BROKER_URL,
    include=['app.tasks.pricing_tasks', 'app.tasks.notifications_tasks']
)

celery.conf.beat_schedule = {
    'fetch-prices-every-minute': {
        'task': 'app.tasks.pricing_tasks.fetch_and_save_prices',
        'schedule': 3,
        'options': {'queue': 'pricing'}
    },
    'check-notifications-every-30-sec': {
        'task': 'app.tasks.notifications_tasks.check_notifications',
        'schedule': 5,
        'options': {'queue': 'notifications'}
    }
}

celery.conf.task_routes = {
    'app.tasks.check_notification': {'queue': 'notifications'},
    'app.tasks.fetch_and_save_prices': {'queue': 'pricing'},
}
