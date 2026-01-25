# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/deribit_db")

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

# Deribit API URL
DERIBIT_API_URL = os.getenv("DERIBIT_API_URL", "https://www.deribit.com/api/v2/")