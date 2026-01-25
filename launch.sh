#!/bin/bash

# Проверка и установка пакетов (если что-то отсутствует, pip установит)
python3 -m pip install -r requirements.txt

# Если установка прошла успешно (exit code 0), запускаем проект
if [ $? -eq 0 ]; then
    echo "All packages are installed or updated. Starting the project..."

    # Запуск FastAPI
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

    # Запуск Celery worker
    celery -A celery_app worker --loglevel=info &

    # Запуск Celery beat (для периодических задач)
    celery -A celery_app beat --loglevel=info &

    # Ждём, пока все процессы не завершатся (Ctrl+C для остановки)
    wait
else
    echo "Package installation failed. Check errors above."
fi