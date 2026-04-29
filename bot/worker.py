import asyncio
import json
import os

import aio_pika
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN', "guest"))

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body)
        num = data.get('message_num', '?')

        print(f" [v] получено сообщение №{num}")

        ticker_name = data['ticker'].replace('_', '-')

        text = (
            f"📊 *Уведомление об изменении цены*\n\n"
            f"💰 Тикер: `{ticker_name}`\n"
            f"📈 Цена: `${data['price']:,}`"
        )

        try:
            await bot.send_message(
                chat_id=data['chat_id'],
                text=text,
                parse_mode="MarkdownV2"
            )
            print(f" [ok] сообщение №{num} успешно отправилось")
        except Exception as e:
            print(f" [!] ошибка при отправке в Telegram: {e}")

async def main():
    rabbit_host = os.getenv("RABBIT_HOST", "localhost")
    connection = await aio_pika.connect_robust(f"amqp://guest:guest@{rabbit_host}/")

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            'notifications.exchange',
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        queue = await channel.declare_queue('notifications.tg.queue', durable=True)
        await queue.bind(exchange, routing_key='notifications.*')

        print(' [*] воркер запущен и ждет сообщений...')

        await queue.consume(process_message)

        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
