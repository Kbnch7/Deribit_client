from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from sqlalchemy.orm import Session

from ..database import get_latest_by_ticker
from ..database.crud import add_notification_to_db
from ..database.session import get_db
from ..middleware.auth import get_current_user
from ..redis import add_notification_to_redis, get_redis
from ..schemas import CreateNotification

notifications_router = APIRouter()

@notifications_router.post("/create")
def create_notification(
    notification_data: CreateNotification,
    current_user: dict = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    current_price = get_latest_by_ticker(db, notification_data.ticker)
    if current_price is None:
        raise HTTPException(status_code=404, detail="No data found for this ticker")

    try:
        user_id = int(current_user.get("sub", 0))
    except (ValueError, TypeError):
        user_id = 0

    payload, direction = add_notification_to_redis(
        redis,
        user_id,
        notification_data.ticker,
        notification_data.target_price,
        current_price.price
    )

    add_notification_to_db(
        db,
        user_id=user_id,
        ticker=notification_data.ticker,
        target_price=notification_data.target_price,
        direction=direction,
        payload=payload
    )

    return {"status": "success", "payload": payload}
