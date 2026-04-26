from typing import List, Optional
from fastapi import Depends, Query, APIRouter, HTTPException, Body
from sqlalchemy.orm import Session
from redis import Redis

from ..redis import get_redis, add_notification_to_redis
from ..database.crud import get_latest_by_ticker, add_notification_to_db
from ..database.session import get_db
from ..schemas import CreateNotification
from ..database import get_latest_by_ticker


notifications_router = APIRouter()

@notifications_router.post("/create")
def create_notification(
    notification_data: CreateNotification,
    # user_id: int = Body(), # TODO: add depends auth
    redis: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    current_price = get_latest_by_ticker(db, notification_data.ticker)
    if current_price is None:
        return HTTPException(status_code=404, detail="No data found for this ticker")
    payload, direction = add_notification_to_redis(redis, 123, notification_data.ticker, notification_data.target_price, current_price.price)
    return payload
