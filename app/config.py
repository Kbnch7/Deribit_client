# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DEBUG: DATABASE_URL is {os.getenv('DATABASE_URL')}")

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")

# Deribit API URL
DERIBIT_API_URL = os.getenv("DERIBIT_API_URL", "https://www.deribit.com/api/v2/")
