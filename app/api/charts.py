from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database.crud import get_all_by_ticker, get_by_ticker_and_date
from ..database.session import get_db
from ..schemas import LinearPriceChart

charts_router = APIRouter()

@charts_router.get("/linear", response_model=list[LinearPriceChart])
def get_all_for_charts(
    ticker: str = Query(..., description="Ticker symbol"),
    limit: int = Query(200, ge=1),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    records = get_all_by_ticker(db, ticker, limit, page)

    data = [
        {"time": r.timestamp, "value": r.price} for r in records if r.price is not None
    ]

    return data[::-1]

@charts_router.get("/linear/get_chart_history")
def get_history(
    ticker: str,
    limit: int = 200,
    before_timestamp: int | None = Query(
        None, description="Unix timestamp самой старой точки на клиенте"
    ),
    db: Session = Depends(get_db)
):
    records = get_by_ticker_and_date(
        db, ticker, start=0, page=1, limit=limit, end=before_timestamp
    )

    data = [
        {"time": r.timestamp, "value": r.price} for r in records if r.price is not None
    ]
    return data[::-1]
