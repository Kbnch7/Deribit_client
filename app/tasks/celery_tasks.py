import time
from celery import shared_task
from ..client.deribit_client import sync_get_index_price
from ..database.crud import create_price_record
from ..database.session import SessionLocal

@shared_task
def fetch_and_save_prices():
    tickers = ['btc_usd', 'eth_usd']
    current_timestamp = int(time.time())
    
    with SessionLocal() as db:
        for ticker in tickers:
            price = sync_get_index_price(ticker)
            if price is not None:
                create_price_record(db, ticker=ticker, price=price, timestamp=current_timestamp)
            else:
                print(f"Failed to fetch price for {ticker}")
    
    return "Prices fetched and saved successfully"