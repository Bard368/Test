import httpx
from core.logger import logger

async def get_weather(city: str) -> str:
    """Отримує розширену погоду через Open-Meteo."""
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=uk"
    logger.info(f"[bold blue]🌍 Геокодування міста:[/bold blue] {city}")

    async with httpx.AsyncClient() as client:
        try:
            geo_resp = await client.get(geo_url, timeout=10.0)
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()

            if "results" not in geo_data:
                return f"Не вдалося знайти координати для міста {city}."

            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            country = geo_data["results"][0]["country"]

            # НОВЕ: Додали apparent_temperature та relative_humidity_2m
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m&timezone=auto"
            weather_resp = await client.get(weather_url, timeout=10.0)
            weather_resp.raise_for_status()
            weather_data = weather_resp.json()

            current = weather_data["current"]
            temp = current["temperature_2m"]
            feels_like = current["apparent_temperature"]
            humidity = current["relative_humidity_2m"]
            wind = current["wind_speed_10m"]

            return (f"Погода в {city} ({country}): {temp}°C (відчувається як {feels_like}°C). "
                    f"Вологість: {humidity}%, швидкість вітру: {wind} км/год.")
        except Exception as e:
            logger.error(f"[bold red]❌ Помилка Open-Meteo:[/bold red] {str(e)}")
            return f"Не вдалося отримати погоду для '{city}'."