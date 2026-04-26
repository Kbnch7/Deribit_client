from app.database.crud import create_price_record, get_latest_by_ticker


def test_create_price_record(db_session):
    record = create_price_record(db_session, "eth_usd", 3000.0, 1700000000)
    assert record.id is not None
    assert record.ticker == "eth_usd"

    latest = get_latest_by_ticker(db_session, "eth_usd")
    assert latest.price == 3000.0

def test_get_all_by_ticker_pagination(db_session):
    from app.database.crud import create_price_record, get_all_by_ticker
    for i in range(10):
        create_price_record(db_session, "btc_usd", 40000.0 + i, 1600000000 + i)

    records = get_all_by_ticker(db_session, "btc_usd", limit=5, page=1)
    assert len(records) == 5
    assert records[0].price == 40009.0
