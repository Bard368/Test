import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    TEMPERATURE: float = 0.2
    
    # Нові ключі
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")

settings = Config()

if not settings.OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не знайдено! Додай його у файл .env")