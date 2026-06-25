import httpx
from core.logger import logger

async def get_exchange_rate(from_currency: str, to_currency: str) -> str:
    """Отримує поточний курс обміну фіатних валют (наприклад: UAH до TRY)."""
    # Використовуємо інше відкрите API, яке підтримує 160+ валют (включно з UAH та TRY)
    url = f"https://open.er-api.com/v6/latest/{from_currency.upper()}"
    logger.info(f"[bold green]💱 Запит фіатного курсу:[/bold green] {from_currency.upper()} -> {to_currency.upper()}")
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Перевірка на помилки від самого API
            if data.get("result") == "error":
                raise ValueError(data.get("error-type", "Unknown API error"))
                
            rates = data.get('rates', {})
            if to_currency.upper() not in rates:
                return f"На жаль, валюту {to_currency.upper()} не знайдено в базі даних."
                
            rate = rates[to_currency.upper()]
            return f"Актуальний курс {from_currency.upper()} до {to_currency.upper()} становить {rate}."
            
        except Exception as e:
            logger.error(f"[bold red]❌ Помилка курсу валют:[/bold red] {str(e)}")
            return f"Не вдалося отримати курс {from_currency} до {to_currency}."