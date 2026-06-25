import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from agent import ChatAgent
from core.logger import logger

console = Console()

async def main():
    console.print(
        Panel.fit(
            "[bold cyan]🤖 AI-Асистент (Ultimate Edition)[/bold cyan]\n\n"
            "Я вмію дізнаватися:\n"
            "🌤️ Погоду в будь-якому місті (Open-Meteo)\n"
            "💵 Курси валют та 🪙 ціни на крипту\n"
            "📊 Акції на фондовому ринку (Finnhub)\n"
            "📰 Свіжі новини та 📚 Вікіпедію\n"
            "⏱️ Точний час у будь-якій точці світу\n"
            "💻 Стан твого комп'ютера (CPU, RAM, Батарея)\n"
            "🔳 Генерувати QR-коди\n"
            "🔗 Скорочувати довгі посилання\n\n"
            "[dim]Для виходу напишіть 'exit' або натисніть Ctrl+C.[/dim]",
            title="Тестове завдання | AI Agent",
            border_style="green"
        )
    )
    
    agent = ChatAgent()
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold yellow]Ви[/bold yellow]")
            
            if user_input.strip().lower() in ['exit', 'quit']:
                console.print("\n[bold green]До зустрічі![/bold green] 👋\n")
                break
                
            if not user_input.strip():
                continue
            
            with console.status("[italic cyan]Асистент аналізує запит...[/italic cyan]", spinner="bouncingBar"):
                answer = await agent.send_message(user_input)
                
            console.print(f"\n[bold magenta]Асистент ›[/bold magenta] {answer}")
            
        except KeyboardInterrupt:
            # Грамотна обробка Ctrl+C без висипання трейсбеку
            console.print("\n\n[bold red]Сеанс перервано користувачем.[/bold red] 👋\n")
            break
        except Exception as e:
            logger.error(f"[bold red]Критична помилка в циклі:[/bold red] {e}")
            # Не перериваємо цикл через одну помилку, даємо можливість продовжити
            console.print("[dim yellow]Спробуйте ще раз або перезапустіть програму.[/dim yellow]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass