# src/intellect_agent/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --- API Key Configuration ---
# Load API keys from environment variables
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
BAIDU_APP_ID = os.getenv("BAIDU_APP_ID")
BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")
TUSHARE_API_KEY = os.getenv("TUSHARE_API_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# --- System Configuration ---

# Redis Configuration (for Celery)
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
