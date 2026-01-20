from aiogram import Bot, Dispatcher
from telesonar.config import TELEGRAM_BOT_TOKEN
from telesonar.handlers.user import user_router
from telesonar.handlers.research import research_router
from telesonar.middlewares.throttling import ThrottlingMiddleware

class TeleSonarBot:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()
        
        self.dp.message.middleware(ThrottlingMiddleware(limit=5.0))
        
        self.dp.include_router(user_router)
        self.dp.include_router(research_router)

    async def start(self):
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

    async def stop(self):
        await self.bot.session.close()
