from sqlalchemy.orm import Session
from sqlalchemy import desc
from .models import PriceRecord

def create_price_record(db: Session, ticker: str, price: float, timestamp: int):
    record = PriceRecord(ticker=ticker, price=price, timestamp=timestamp)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_all_by_ticker(db: Session, ticker: str, limit: int = 5, page: int = 1):
    return db.query(PriceRecord).filter(PriceRecord.ticker == ticker).order_by(desc(PriceRecord.timestamp)).offset((page - 1) * limit).limit(limit).all()

def get_latest_by_ticker(db: Session, ticker: str):
    return db.query(PriceRecord).filter(PriceRecord.ticker == ticker).order_by(desc(PriceRecord.timestamp)).first()

def get_by_ticker_and_date(db: Session, ticker: str, start: int, limit: int, page: int, end: int = None):
    query = db.query(PriceRecord).filter(PriceRecord.ticker == ticker, PriceRecord.timestamp >= start)
    if end:
        query = query.filter(PriceRecord.timestamp <= end)
    query = query.offset((page - 1) * limit).limit(limit)
    return query.all()
