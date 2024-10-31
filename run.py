from typing import Any
from logger import logger
from bot.handlers import router
from aiogram import Bot, Dispatcher
from config import bot_token, bot_logger_token, admin


bot = Bot(bot_token)
bot_logger = Bot(bot_logger_token)
dp = Dispatcher()


async def main() -> Any:
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=False)


async def send_log() -> Any:
    with open('bot.log', 'r', encoding='utf-8') as f:
        f.seek(0, 2)
        while True:
            new_line = f.readlines()
            if new_line:
                for line in new_line:
                    await bot_logger.send_message(chat_id=admin, text=line.strip())
            await asyncio.sleep(1)


async def start() -> Any:
    await asyncio.gather(main(), send_log())


if __name__ == '__main__':
    import asyncio
    logger.info('Бот запущен.')
    asyncio.run(start())
