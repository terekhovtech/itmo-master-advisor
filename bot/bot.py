import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from scraper.scraper import update_if_needed
from agent.agent import answer_question

load_dotenv()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set in environment")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я помогаю выбрать магистратуру между AI и AI Product (ИТМО).\nКоманды: /refresh — обновить данные. Просто задайте вопрос по программам, например: 'Какие выборные курсы полезны для MLOps?'")

@dp.message(Command('refresh'))
async def cmd_refresh(message: types.Message):
    await message.answer("Обновляю данные с сайтов...")
    try:
        for k in ["ai", "ai_product"]:
            update_if_needed(k)
        await message.answer("Готово — данные обновлены.")
    except Exception as e:
        await message.answer(f"Ошибка при обновлении: {e}")

@dp.message()
async def handle_text(message: types.Message):
    txt = message.text.strip()
    # simple routing: check if user mentions program
    if "product" in txt.lower():
        prog = "ai_product"
    else:
        prog = "ai"
    await message.chat.do("typing")
    try:
        ans = answer_question(prog, txt)
        await message.answer(ans)
    except Exception as e:
        await message.answer(f"Ошибка агента: {e}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))
