import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from worker import process_message


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "123456:fake_token")
    monkeypatch.setenv("RABBIT_HOST", "localhost")
    monkeypatch.setenv("LOGIN", "guest")

@pytest.mark.asyncio
async def test_process_message_success():
    test_data = {
        'message_num': 42,
        'ticker': 'BTC_USDT',
        'price': 50000,
        'chat_id': 123456789
    }
    message_body = json.dumps(test_data).encode('utf-8')

    mock_message = MagicMock()
    mock_message.body = message_body
    mock_message.process.return_value.__aenter__ = AsyncMock()
    mock_message.process.return_value.__aexit__ = AsyncMock()

    with patch('worker.bot.send_message', new_callable=AsyncMock) as mock_send:

        await process_message(mock_message)

        mock_message.process.return_value.__aenter__.assert_called_once()

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args

        assert kwargs['chat_id'] == 123456789
        assert "BTC-USDT" in kwargs['text']
        assert "50,000" in kwargs['text']
        assert kwargs['parse_mode'] == "MarkdownV2"

@pytest.mark.asyncio
async def test_process_message_error_handling():
    test_data = {
        'message_num': 1,
        'ticker': 'ETH_USDT',
        'price': 3000,
        'chat_id': 0
    }
    mock_message = MagicMock()
    mock_message.body = json.dumps(test_data).encode('utf-8')
    mock_message.process.return_value.__aenter__ = AsyncMock()
    mock_message.process.return_value.__aexit__ = AsyncMock()

    with patch('worker.bot.send_message', side_effect=Exception("Telegram Error")):
        await process_message(mock_message)

        mock_message.process.return_value.__aenter__.assert_called_once()

@pytest.mark.asyncio
async def test_main_connection_setup(mocker):
    mock_connect = mocker.patch('aio_pika.connect_robust', new_callable=AsyncMock)
    mock_connection = mock_connect.return_value
    mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
    mock_connection.__aexit__ = AsyncMock()

    mock_channel = AsyncMock()
    mock_connection.channel.return_value = mock_channel

    mocker.patch('asyncio.Future', side_effect=asyncio.CancelledError)

    from worker import main
    try:
        await main()
    except asyncio.CancelledError:
        pass

    mock_connect.assert_called()
    mock_channel.declare_queue.assert_called_with(
        'notifications.tg.queue', durable=True
    )
    mock_channel.declare_exchange.assert_called_with(
        'notifications.exchange',
        'topic',
        durable=True
    )
