import os

import redis

redis_url = os.getenv('REDIS_NOTIFICATIONS_URL')

def get_redis():
    db = redis.from_url(redis_url, decode_responses=True)
    try:
        yield db
    finally:
        db.close()
