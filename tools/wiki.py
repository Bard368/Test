import httpx
import urllib.parse
from core.logger import logger

async def search_wikipedia(query: str) -> str:
    """Шукає інформацію у Вікіпедії (чесний User-Agent + правильне кодування)."""
    # 1. Правильно кодуємо пробіли та кирилицю (Сеул -> %D0%A1%D0%B5%D1%83%D0%BB)
    encoded_query = urllib.parse.quote(query.replace(' ', '_'))
    
    # 2. ВАЖЛИВО: Вікіпедія БЛОКУЄ фейкові "Mozilla/5.0". Вони вимагають чесний User-Agent!
    headers = {
        "User-Agent": "MyPersonalAIAgent/1.0 (contact: test_agent@example.com)"
    }
    
    logger.info(f"[bold magenta]📚 Запит до Вікіпедії:[/bold magenta] {query}")

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            # Спочатку шукаємо в українській Вікіпедії
            url_uk = f"https://uk.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
            response = await client.get(url_uk, timeout=10.0)
            
            # Якщо немає укр, шукаємо в російській
            if response.status_code == 404:
                url_ru = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
                response = await client.get(url_ru, timeout=10.0)
                
                # Якщо немає і там, переходимо на англійську
                if response.status_code == 404:
                    url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
                    response = await client.get(url_en, timeout=10.0)
                    
                    if response.status_code == 404:
                        return f"На жаль, за запитом '{query}' у Вікіпедії нічого не знайдено."

            response.raise_for_status()
            data = response.json()

            summary = data.get('extract', 'Немає детального опису.')
            return f"Довідка з Вікіпедії: {summary}"

        except Exception as e:
            logger.error(f"[bold red]❌ Помилка Вікіпедії:[/bold red] {str(e)}")
            return "Не вдалося отримати дані з Вікіпедії через помилку з'єднання."