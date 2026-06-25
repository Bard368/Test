import httpx
from core.logger import logger

async def shorten_url(long_url: str) -> str:
    """Скорочує довге посилання за допомогою безкоштовного API TinyURL."""
    logger.info(f"[bold magenta]🔗 Скорочення посилання:[/bold magenta] {long_url}")
    url = f"https://tinyurl.com/api-create.php?url={long_url}"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            short_url = response.text
            return f"Ось твоє скорочене посилання: {short_url}"
        except Exception as e:
            logger.error(f"[bold red]❌ Помилка скорочення URL:[/bold red] {str(e)}")
            return "Не вдалося скоротити посилання. Перевір, чи правильний URL ти надав."