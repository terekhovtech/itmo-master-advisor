# ITMO Master Advisor

Это минимальный рабочий пример проекта: парсер учебных планов ИТМО, Telegram-бот и агент с подключением к OPENOPENROUTER API.
Архив содержит MVP — рабочий каркас. Требует заполнения `.env` c `TELEGRAM_TOKEN` и `OPENOPENROUTER_APIAI_API_KEY`.

## Быстрый старт (локально)
1. Склонируйте/распакуйте репозиторий.
2. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Linux / macOS
   .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```
3. Создайте файл в корневой директории `.env` и заполните переменные:
   - TELEGRAM_TOKEN — токен бота Telegram
   - OPENROUTER_API — ключ OPENROUTER API
4. Запустите бота:
   ```bash
   python bot/bot.py
   ```
5. В Telegram найдите своего бота и используйте команды:
   - `/start` — старт
   - `/refresh` — форсировать обновление данных (парсер)
   - потом задавайте вопросы обычным сообщением

## Структура
- `scraper/` — простой парсер двух страниц и сохранение JSON в `data/`
- `agent/` — реализация поиска через OpenAI embeddings и базовый QA
- `bot/` — aiogram-бот, интеграция с agent/scraper
- `data/` — место для сохранённых JSON
