def test_get_tickers_list_empty(client):
    response = client.get("/api/tickers_list")
    assert response.status_code == 200
    assert response.json() == []

def test_get_latest_no_data(client):
    response = client.get("/api/latest?ticker=btc_usd")
    assert response.status_code == 404
    assert response.json()["detail"] == "No data found for this ticker"

def test_create_and_get_price(client, db_session):
    from app.database.crud import create_price_record
    create_price_record(
        db_session, ticker="btc_usd", price=50000.0, timestamp=1600000000
    )

    response = client.get("/api/latest?ticker=btc_usd")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "btc_usd"
    assert data["price"] == 50000.0
