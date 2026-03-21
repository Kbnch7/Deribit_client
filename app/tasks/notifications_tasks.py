from celery import shared_task
import aio_pika
import redis

from app.redis import get_notifications_from_redis
from app.database.crud import get_latest_by_ticker
from app.database.session import SessionLocal

import os
import json
import asyncio

rabbit_url = os.getenv("RABBITMQ_URL")
tickers = os.getenv("TICKERS_NOTIFICATIONS").split(",")

async def async_check_notifications():
    connection = await aio_pika.connect_robust(rabbit_url)
    db = SessionLocal()
    redis_url = os.getenv("REDIS_NOTIFICATIONS_URL", "redis://redis_notifications:6379/0")
    redis_client = redis.from_url(redis_url, decode_responses=True)
    async with connection:
        channel = await connection.channel()
        async with channel:
            exchange = await channel.declare_exchange(
                'notifications.exchange', 
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            queue = await channel.declare_queue('notifications.tg.queue', durable=True)
            await queue.bind(exchange, routing_key='notifications.*')

            for ticker in tickers:
                price = get_latest_by_ticker(db, ticker)
                notifications = get_notifications_from_redis(redis_client, ticker, price.price)

                for notification in notifications:
                    notification_json = json.loads(notification)
                    data = {
                        "ticker": notification_json["ticker"],
                        "price": notification_json["target_price"],
                        "chat_id": notification_json["user_id"]
                    }

                    message_body = json.dumps(data).encode()
                    await exchange.publish(
                        aio_pika.Message(
                            body=message_body,
                            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                        ),
                        routing_key='notifications.telegram'
                    )

@shared_task
def check_notifications():
    asyncio.run(async_check_notifications())