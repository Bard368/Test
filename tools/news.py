import httpx
from core.config import settings
from core.logger import logger

async def get_latest_news(topic: str) -> str:
    """Шукає останні новини та повертає їх з посиланнями."""
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&pageSize=3&apiKey={settings.NEWS_API_KEY}"
    logger.info(f"[bold magenta]📰 Запит новин:[/bold magenta] {topic}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            if data.get("totalResults", 0) == 0:
                return f"За темою '{topic}' свіжих новин не знайдено."

            articles = data["articles"]
            news_summary = f"Ось останні новини за темою '{topic}':\n\n"
            
            for i, article in enumerate(articles, 1):
                title = article.get("title", "Без заголовка")
                source = article.get("source", {}).get("name", "Невідоме джерело")
                url = article.get("url", "#")
                # НОВЕ: Додали клікабельне посилання
                news_summary += f"{i}. {title}\nДжерело: {source} | Читати: {url}\n\n"

            return news_summary.strip()
        except Exception as e:
            logger.error(f"[bold red]❌ Помилка NewsAPI:[/bold red] {str(e)}")
            return f"Не вдалося завантажити новини за темою '{topic}'."