import httpx
from core.config import settings
from core.logger import logger

async def get_stock_price(ticker: str) -> str:
    """Отримує глибоку статистику акції через Finnhub."""
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker.upper()}&token={settings.FINNHUB_API_KEY}"
    logger.info(f"[bold blue]📊 Запит Finnhub:[/bold blue] {ticker.upper()}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            if data.get("c") == 0 and data.get("d") is None:
                return f"Тікер {ticker.upper()} не знайдено."

            current_price = data['c']
            change_percent = data['dp']
            high_day = data['h']
            low_day = data['l']
            open_price = data['o']

            trend = "зросла 📈" if change_percent > 0 else "впала 📉"
            
            return (f"Деталі по акції {ticker.upper()}:\n"
                    f"💵 Поточна ціна: {current_price} USD ({trend} на {change_percent}%)\n"
                    f"📊 Ціна відкриття: {open_price} USD\n"
                    f"⬆️ Максимум за день: {high_day} USD\n"
                    f"⬇️ Мінімум за день: {low_day} USD")
        except Exception as e:
            logger.error(f"[bold red]❌ Помилка Finnhub:[/bold red] {str(e)}")
            return f"Не вдалося отримати дані для {ticker.upper()}."