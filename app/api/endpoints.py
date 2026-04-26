
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database.crud import (
    get_all_by_ticker,
    get_all_ticker_names,
    get_by_ticker_and_date,
    get_latest_by_ticker,
)
from ..database.session import get_db
from ..schemas import PriceResponse, TickerName

api_router = APIRouter()

@api_router.get("/all", response_model=list[PriceResponse])
def get_all(
    ticker: str = Query(..., description="Ticker symbol (e.g., btc_usd or eth_usd)"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    return get_all_by_ticker(db, ticker, limit, page)

@api_router.get("/latest", response_model=PriceResponse)
def get_latest(
    ticker: str = Query(..., description="Ticker symbol (e.g., btc_usd or eth_usd)"),
    db: Session = Depends(get_db)
):
    latest = get_latest_by_ticker(db, ticker)
    if not latest:
        raise HTTPException(status_code=404, detail="No data found for this ticker")
    return latest

@api_router.get("/by_date", response_model=list[PriceResponse])
def get_by_date(
    ticker: str = Query(..., description="Ticker symbol (e.g., btc_usd or eth_usd)"),
    start: int = Query(..., description="Start UNIX timestamp"),
    end: int | None = Query(None, description="End UNIX timestamp (optional)"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1),
    db: Session = Depends(get_db)
):
    return get_by_ticker_and_date(db, ticker, start, limit, page, end)

@api_router.get("/tickers_list", response_model=list[TickerName])
def get_all_tickers(
    db: Session = Depends(get_db)
):
    ticker_names = get_all_ticker_names(db)
    return [{"name": row.ticker} for row in ticker_names]
