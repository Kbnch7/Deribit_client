from sqlalchemy import desc
from sqlalchemy.orm import Session

from .models import Notification, PriceRecord


def create_price_record(db: Session, ticker: str, price: float, timestamp: int):
    record = PriceRecord(ticker=ticker, price=price, timestamp=timestamp)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_all_by_ticker(db: Session, ticker: str, limit: int = 5, page: int = 1):
    return db.query(
        PriceRecord
    ).filter(
        PriceRecord.ticker == ticker
    ).order_by(
        desc(PriceRecord.timestamp)
    ).offset((page - 1) * limit).limit(limit).all()

def get_latest_by_ticker(db: Session, ticker: str):
    return db.query(
        PriceRecord
    ).filter(PriceRecord.ticker == ticker).order_by(desc(PriceRecord.timestamp)).first()

def get_by_ticker_and_date(
        db: Session, ticker: str, start: int, limit: int, page: int, end: int = None
    ):
    query = db.query(PriceRecord).filter(
        PriceRecord.ticker == ticker,
        PriceRecord.price.isnot(None)
    )

    if start:
        query = query.filter(PriceRecord.timestamp >= start)

    if end:
        query = query.filter(PriceRecord.timestamp < end)

    query = query.order_by(desc(PriceRecord.timestamp))

    query = query.offset((page - 1) * limit).limit(limit)

    return query.all()

def get_all_ticker_names(db: Session):
    data = db.query(PriceRecord.ticker).distinct()
    return data

def add_notification_to_db(
        db: Session,
        user_id: int,
        ticker: str,
        target_price: float,
        direction: str,
        payload: str
    ):
    notification = Notification(
        user_id=user_id,
        ticker=ticker,
        target_price=target_price,
        direction=direction,
        payload=payload
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
