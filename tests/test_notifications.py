from unittest.mock import MagicMock

from app.main import app
from app.middleware.auth import get_current_user
from app.redis.session import get_redis


def test_create_notification_unauthorized(client):
    response = client.post(
        "/api/notifications/create", json={"ticker": "btc_usd", "target_price": 60000}
    )
    assert response.status_code == 401

def test_create_notification_success(client, db_session):
    app.dependency_overrides[
        get_current_user
    ] = lambda: {"sub": "1", "name": "testuser"}
    mock_redis = MagicMock()
    app.dependency_overrides[get_redis] = lambda: mock_redis


    from app.database.crud import create_price_record
    create_price_record(db_session, "btc_usd", 55000.0, 1600000000)

    payload = {"target_price": 60000, "ticker": "btc_usd"}
    response = client.post("/api/notifications/create", json=payload)

    assert response.status_code == 200
    assert mock_redis.zadd.called
