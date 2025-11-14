# src/intellect_agent/config.py

# --- API Key Configuration ---
# Replace the placeholder values with your actual API keys.

# Social Media & Scraping
APIFY_API_KEY = "YOUR_APIFY_API_KEY_HERE"

# AI & NLP
BAIDU_APP_ID = "YOUR_BAIDU_APP_ID_HERE"
BAIDU_API_KEY = "YOUR_BAIDU_API_KEY_HERE"
BAIDU_SECRET_KEY = "YOUR_BAIDU_SECRET_KEY_HERE"

# Financial Data
TUSHARE_API_KEY = "YOUR_TUSHARE_API_KEY_HERE"
FMP_API_KEY = "YOUR_FMP_API_KEY_HERE" # Fallback

# News
NEWS_API_KEY = "YOUR_NEWS_API_KEY_HERE"

# --- System Configuration ---

# Redis Configuration (for Celery)
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
