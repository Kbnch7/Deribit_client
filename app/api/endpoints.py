from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..database.crud import (
    get_all_by_ticker,
    get_latest_by_ticker,
    get_by_ticker_and_date
)

router = APIRouter()

class PriceResponse(BaseModel):
    ticker: str
    price: float
    timestamp: int

    class Config:
        from_attributes = True

@router.get("/all", response_model=List[PriceResponse])
def get_all(
    ticker: str = Query(..., description="Ticker symbol (e.g., btc_usd or eth_usd)"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    return get_all_by_ticker(db, ticker, limit, page)

@router.get("/latest", response_model=PriceResponse)
def get_latest(
    ticker: str = Query(..., description="Ticker symbol (e.g., btc_usd or eth_usd)"),
    db: Session = Depends(get_db)
):
    latest = get_latest_by_ticker(db, ticker)
    if not latest:
        raise HTTPException(status_code=404, detail="No data found for this ticker")
    return latest

@router.get("/by_date", response_model=List[PriceResponse])
def get_by_date(
    ticker: str = Query(..., description="Ticker symbol (e.g., btc_usd or eth_usd)"),
    start: int = Query(..., description="Start UNIX timestamp"),
    end: Optional[int] = Query(None, description="End UNIX timestamp (optional)"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    return get_by_ticker_and_date(db, ticker, start, limit, page, end)
