from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey
import asyncio

# Настройка конфигурации
config = YandexGPTConfigManagerForAPIKey(
    model_type="yandexgpt",  # или "yandexgpt-lite"
    catalog_id="ваш_catalog_id",
    api_key="ваш_api_key"
)

# Инициализация клиента
yandex_gpt = YandexGPT(config_manager=config)

# Асинхронная функция для получения ответа
async def get_completion():
    messages = [{"role": "user", "text": "Привет! Расскажи интересный факт."}]
    completion = await yandex_gpt.get_async_completion(messages=messages)
    print("Ответ YandexGPT:", completion)

# Запуск асинхронной функции
asyncio.run(get_completion())
