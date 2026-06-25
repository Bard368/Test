import httpx
from core.logger import logger

async def get_crypto_price(symbol: str) -> str:
    """Отримує поточну ціну криптовалюти в USDT (наприклад: BTC, ETH, SOL)."""
    formatted_symbol = f"{symbol.upper()}USDT"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={formatted_symbol}"
    logger.info(f"[bold yellow]📈 Запит крипто-маркету:[/bold yellow] {formatted_symbol}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            price = round(float(data['price']), 2)
            return f"Поточна ціна {symbol.upper()} на ринку: {price} USDT."
        except Exception as e:
            logger.error(f"[bold red]❌ Помилка крипто-курсу:[/bold red] {str(e)}")
            return f"Не вдалося знайти ціну для криптовалюти {symbol.upper()}."