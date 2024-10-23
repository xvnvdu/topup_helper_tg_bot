from typing import Any
from logger import logger
from config import bot_token
from bot.handlers import router
from aiogram import Bot, Dispatcher


bot = Bot(bot_token)
dp = Dispatcher()


async def main() -> Any:
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=False)


if __name__ == '__main__':
    import asyncio
    logger.info('Бот запущен.')
    asyncio.run(main())

