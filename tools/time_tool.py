import httpx
from core.logger import logger

async def get_current_time(timezone: str) -> str:
    """Отримує час через стабільний сервіс TimeAPI.io."""
    # API вимагає формат IANA (наприклад: Asia/Seoul, Europe/Paris)
    url = f"https://timeapi.io/api/Time/current/zone?timeZone={timezone}"
    logger.info(f"[bold cyan]⏱️ Запит світового часу:[/bold cyan] {timezone}")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            date_str = data.get("date", "")
            time_str = data.get("time", "")
            return f"Поточний час у зоні {timezone}: {date_str}, {time_str}."
        except Exception as e:
            logger.error(f"[bold red]❌ Помилка часу:[/bold red] {str(e)}")
            return f"Не вдалося отримати час. Перевірте, чи правильно вказано часовий пояс (наприклад, Asia/Seoul)."