import json
import asyncio
from openai import AsyncOpenAI
from core.config import settings
from core.logger import logger

# --- ІМПОРТ ВСІХ ІНСТРУМЕНТІВ ---
from tools.weather import get_weather
from tools.currency import get_exchange_rate
from tools.crypto import get_crypto_price
from tools.time_tool import get_current_time
from tools.stocks import get_stock_price
from tools.news import get_latest_news
from tools.wiki import search_wikipedia
from tools.hardware import get_system_status
from tools.qr_generator import generate_qr_code
from tools.url_shortener import shorten_url

class ChatAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.MODEL
        self.max_history_length = 20
        
        self.history = [
            {
                "role": "system",
                "content": (
                    "Ти — суперинтелектуальний AI-помічник. Спілкуйся українською мовою. "
                    "Вмієш підтримати розмову, але для будь-яких фактичних чи технічних задач "
                    "ЗАВЖДИ викликай інструменти. "
                    "ВАЖЛИВО: Ти працюєш ЛОКАЛЬНО на комп'ютері користувача. "
                    "Якщо інструмент зберігає файл (наприклад QR-код), ти НЕ ПОВИНЕН генерувати лінки на 'sandbox'. "
                    "Просто напиши користувачу: 'Файл збережено за адресою: [шлях_до_файлу]'. "
                    "Більше ніяких посилань на скачування!"
                )
            }
        ]
        
        # Реєструємо функції у словнику
        self.available_tools = {
            "get_weather": get_weather,
            "get_exchange_rate": get_exchange_rate,
            "get_crypto_price": get_crypto_price,
            "get_current_time": get_current_time,
            "get_stock_price": get_stock_price,
            "get_latest_news": get_latest_news,
            "search_wikipedia": search_wikipedia,
            "get_system_status": get_system_status,
            "generate_qr_code": generate_qr_code,
            "shorten_url": shorten_url
        }
        
        # Схеми інструментів для OpenAI
        self.tools_schema = [
            {"type": "function", "function": {"name": "get_weather", "description": "Погода", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
            {"type": "function", "function": {"name": "get_exchange_rate", "description": "Курс фіатних валют", "parameters": {"type": "object", "properties": {"from_currency": {"type": "string"}, "to_currency": {"type": "string"}}, "required": ["from_currency", "to_currency"]}}},
            {"type": "function", "function": {"name": "get_crypto_price", "description": "Ціна крипти", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}}},
            {"type": "function", "function": {"name": "get_current_time", "description": "Час за часовим поясом.", "parameters": {"type": "object", "properties": {"timezone": {"type": "string", "description": "Наприклад: Europe/Kyiv, Asia/Seoul"}}, "required": ["timezone"]}}},
            {"type": "function", "function": {"name": "get_stock_price", "description": "Ціна акції (Finnhub).", "parameters": {"type": "object", "properties": {"ticker": {"type": "string", "description": "Тікер, наприклад AAPL"}}, "required": ["ticker"]}}},
            {"type": "function", "function": {"name": "get_latest_news", "description": "Останні новини (NewsAPI).", "parameters": {"type": "object", "properties": {"topic": {"type": "string", "description": "Тема новин"}}, "required": ["topic"]}}},
            {"type": "function", "function": {"name": "search_wikipedia", "description": "Довідка з Вікіпедії.", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Що шукати"}}, "required": ["query"]}}},
            
            # --- НОВІ СУПЕР-ІНСТРУМЕНТИ ---
            {"type": "function", "function": {"name": "get_system_status", "description": "Отримати інформацію про завантаження CPU, RAM та батареї поточного комп'ютера.", "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "generate_qr_code", "description": "Згенерувати QR-код і зберегти як картинку.", "parameters": {"type": "object", "properties": {"data": {"type": "string", "description": "Текст або URL для зашифровки"}, "filename": {"type": "string", "description": "Назва файлу, наприклад my_qr.png"}}, "required": ["data"]}}},
            {"type": "function", "function": {"name": "shorten_url", "description": "Скоротити довге посилання.", "parameters": {"type": "object", "properties": {"long_url": {"type": "string", "description": "Оригінальний довгий URL"}}, "required": ["long_url"]}}}
        ]

    def _trim_history(self):
        if len(self.history) > self.max_history_length:
            self.history = [self.history[0]] + self.history[-(self.max_history_length - 1):]

    async def _execute_tool(self, tool_call):
        func_name = tool_call.function.name
        try:
            func_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return tool_call.id, func_name, "Помилка парсингу."

        logger.info(f"[dim]⚡ Виконую:[/dim] {func_name}({func_args})")
        
        if func_name in self.available_tools:
            try:
                result = await self.available_tools[func_name](**func_args)
                return tool_call.id, func_name, str(result)
            except Exception as e:
                return tool_call.id, func_name, f"Помилка: {str(e)}"
                
        return tool_call.id, func_name, "Функцію не знайдено."

    async def send_message(self, user_text: str):
        self.history.append({"role": "user", "content": user_text})
        self._trim_history()
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            tools=self.tools_schema,
            temperature=settings.TEMPERATURE
        )
        
        response_message = response.choices[0].message
        self.history.append(response_message)
        
        if response_message.tool_calls:
            tasks = [self._execute_tool(tc) for tc in response_message.tool_calls]
            results = await asyncio.gather(*tasks)
            
            for tool_call_id, func_name, tool_output in results:
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": func_name,
                    "content": tool_output
                })
            
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                temperature=settings.TEMPERATURE
            )
            final_text = final_response.choices[0].message.content
            self.history.append({"role": "assistant", "content": final_text})
            return final_text
            
        return response_message.content