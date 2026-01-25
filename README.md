# README.md

## Введение

Добрый день! Это репозиторий с выполнением тестового задания на позицию Junior Backend Developer. Проект представляет собой полноценное приложение для мониторинга цен криптовалют (BTC_USD и ETH_USD) с биржи Deribit. Я реализовал клиент для получения данных, хранение в PostgreSQL, внешнее API на FastAPI и периодические задачи с Celery. Всё сделано с акцентом на чистую архитектуру, правильный нейминг, отсутствие глобальных переменных и использование ООП — как и требовалось в критериях оценки.

Я не просто выполнил обязательные требования, но и реализовал необязательные: контейнеризацию в Docker (с отдельными контейнерами для app, DB, Redis и Celery), и асинхронный клиент на aiohttp. В итоге получился профессиональный, масштабируемый проект, который легко развернуть и поддерживать. Я горжусь тем, как получилось — код чистый, читаемый, и все решения обоснованы в секции Design Decisions.

## Выполненные требования

### Обязательные требования
- **Клиент для Deribit**: Реализован класс `DeribitClient` (в `app/client/deribit_client.py`), который запрашивает index price для `btc_usd` и `eth_usd`. Данные сохраняются в DB каждую минуту (ticker, price, UNIX timestamp).
- **API на FastAPI**: Создано внешнее API с тремя GET-методами:
  - `/api/all?ticker=<ticker>`: Получение всех сохранённых данных по валюте.
  - `/api/latest?ticker=<ticker>`: Получение последней цены.
  - `/api/by_date?ticker=<ticker>&start=<timestamp>&end=<timestamp>`: Получение цен с фильтром по дате (start/end в UNIX timestamp, end опционально).
  Все методы используют обязательный query-параметр `ticker` и возвращают JSON с валидацией через Pydantic.
- **База данных**: Использована PostgreSQL с SQLAlchemy. Модель `PriceRecord` (id, ticker, price, timestamp). CRUD-операции в `app/database/crud.py`.
- **Celery для периодических задач**: Настроен Celery с Redis как брокером. Задача `fetch_and_save_prices` запускается каждые 60 секунд (beat scheduler). Нет блокировки основного приложения.
- **README и документация**: Этот файл! Секция Design Decisions ниже. Инструкции по разворачиванию — в отдельном разделе.

### Необязательные требования
- **Развёртывание в контейнерах**: Приложение в Docker с двумя основными контейнерами (app + db), плюс Redis и отдельные для Celery worker/beat (для масштабируемости). `docker-compose.yml` запускает всё одной командой.
- **aiohttp для клиента**: Клиент асинхронный на aiohttp для эффективности. Добавлена sync-обертка для интеграции с Celery (обоснование в Design Decisions).

### Критерии оценки
- **Чистая архитектура/чистый код**: Разделение на модули (client, database, api, tasks). SRP (Single Responsibility Principle) везде.
- **Нейминг**: Snake_case для функций/переменных, CamelCase для классов. Описательные имена (e.g., `get_latest_by_ticker`, `sync_get_index_price`).
- **Отсутствие глобальных переменных**: Все настройки в `config.py` (из .env)
- **ООП**: Классы для клиента (`DeribitClient`), моделей (`PriceRecord`), CRUD как функции с сессиями (но можно расширить на классы).
- **Понимание решений**: Всё объяснено в Design Decisions.

## Структура проекта

```
deribit_test_task/
├── app/                  # Основное приложение
│   ├── __init__.py
│   ├── main.py           # Точка входа FastAPI
│   ├── config.py         # Настройки (.env)
│   ├── client/           # Клиент Deribit (aiohttp)
│   ├── database/         # SQLAlchemy модели, CRUD, сессии
│   ├── api/              # Эндпоинты FastAPI
│   └── tasks/            # Celery задачи
├── celery_app.py         # Инициализация Celery
├── static/               # Простой frontend (HTML/JS для демонстрации API)
├── Dockerfile            # Для сборки app
├── docker-compose.yml    # Развёртывание (app, db, redis, celery)
├── requirements.txt      # Зависимости
├── .env.                 # Т.к. это учебный проект/тз и никаких секретных ключей я не использую, выложил .env
├── .gitignore            # Игнор venv, logs etc.
└── README.md             # Этот файл
```

## Design Decisions (Решения по дизайну)

Я стремился к чистой, модульной архитектуре, чтобы проект был легко расширяемым и тестируемым. Вот ключевые решения и их обоснование:

1. **Архитектура**: Разделил на слои (client для внешних API, database, api, tasks). Это соответствует Clean Architecture.Обоснование: Упрощает maintenance и scaling (e.g., добавить больше тикеров).

2. **Клиент на aiohttp**: Выбрал асинхронный подход для производительности (необязательное требование). Добавил sync-обертку (`sync_get_index_price`), чтобы интегрировать с sync Celery без проблем event loop. Обоснование: Асинхронность позволяет параллельные запросы в будущем, но не усложняет текущий код.

3. **Celery + Redis**: Celery для periodic tasks (every 60s) — идеально для фоновых jobs без блокировки API. Redis как broker (простой, надёжный). Beat scheduler для расписания. Обоснование: Избегает cron или loop в app

4. **DB и SQLAlchemy**: PostgreSQL для relational data (индексы на ticker/timestamp для быстрых запросов). SQLAlchemy ORM для ООП (модели как классы). CRUD функции с сессиями (Depends в FastAPI). Обоснование:  легко мигрировать (можно добавить Alembic), performance для фильтров по дате.

5. **FastAPI и Pydantic**: Для API — быстрое, с auto-docs (/docs). Response models для валидации. Query params с валидацией (e.g., int для timestamp). Обоснование: Современный фреймворк, async-ready, built-in Swagger для docs.

6. **Контейнеризация**: Docker-compose с отдельными сервисами (app, db, redis, celery_worker, celery_beat). Healthchecks для зависимостей. Обоснование: Reproducibility, easy deploy (e.g., на VPS). Выполняет необязательное требование "в двух контейнерах" (app + db базово, + расширил).

7. **Дополнительно**: Добавил простой frontend (static/index.html) для demo API — не в ТЗ, но полезно для визуализации. CORS middleware для cross-origin requests.

Все решения основаны на best practices: KISS (Keep It Simple), DRY (Don't Repeat Yourself), и фокус на performance/scalability.

## Инструкции по разворачиванию

### Локальный запуск
1. Клонируйте репозиторий: `git clone <gitlab-url>`.
2. Создайте venv: `python -m venv venv && source venv/bin/activate`.
3. Установите зависимости: `pip install -r requirements.txt`.
4. Настройте .env (скопируйте из .env.example):
   - `DATABASE_URL=postgresql://user:password@localhost:5432/deribit_db`
   - `CELERY_BROKER_URL=redis://localhost:6379/0`
   - `DERIBIT_API_URL=https://www.deribit.com/api/v2`
5. Запустите Postgres и Redis локально (или в Docker: `docker run -d -p 5432:5432 --name pg postgres` и аналогично для Redis).
6. Создайте DB: В psql — `CREATE DATABASE deribit_db;`.
7. Запустите: `./launch.sh` (установит пакеты, запустит uvicorn, celery worker/beat).
8. API на http://localhost:8000/docs. Frontend: http://localhost:8000/static/index.html.

### Запуск в Docker
1. Настройте .env (как выше).
2. Соберите и запустите: `docker-compose up --build -d`.
3. API на http://localhost:8000/docs. Ждите 1-2 мин, пока Celery fetch'нет цены.
4. Logs: `docker-compose logs -f`.
5. Остановка: `docker-compose down`.

## API Документация
- Swagger: /docs (авто-генерируется FastAPI).
- Примеры запросов (curl):
  - All: `curl "http://localhost:8000/api/all?ticker=btc_usd&page=&limit="`
  - Latest: `curl "http://localhost:8000/api/latest?ticker=eth_usd"`
  - By date: `curl "http://localhost:8000/api/by_date?ticker=btc_usd&start=&end=&page=&limit="`
