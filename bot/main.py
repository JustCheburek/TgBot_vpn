"""Main entry point for the VPN Telegram Bot"""

import logging
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config.settings import Config
from bot.models.database import DatabaseManager
from bot.handlers.main import router as main_router
from bot.handlers.admin import router as admin_router
from bot.middlewares.db import DbSessionMiddleware
from bot.utils.helpers import setup_logging

# Configure logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Post initialization tasks"""
    logger.info("🚀 VPN Bot initialization started")

    # Initialize database
    db_manager = DatabaseManager(Config.DATABASE_URL)
    db_manager.create_tables()

    # Initialize bot and dispatcher
    bot = Bot(token=Config.BOT_TOKEN)

    # Using memory storage for FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register middleware
    dp.update.middleware(DbSessionMiddleware(db_manager))

    # Register routers
    dp.include_router(admin_router)
    dp.include_router(main_router)

    # Set up startup and shutdown handlers
    @dp.startup()
    async def on_startup():
        logger.info("Bot is starting up...")
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot started: @{bot_info.username}")

        # Send startup message to admins
        startup_message = (
            "🤖 <b>VPN Bot запущен успешно!</b>\n\n"
            f"🆔 Бот: @{bot_info.username}\n"
            f"📅 Время запуска: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n"
            f"⚙️ Режим отладки: {'✅' if Config.DEBUG else '❌'}\n"
            f"🗄️ База данных: {'✅ Подключена' if db_manager else '❌ Ошибка'}\n\n"
            "🎯 Бот готов к работе с пользователями!"
        )

        # Notify admins
        for admin_id in Config.ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=startup_message,
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.warning(f"Failed to notify admin {admin_id}: {e}")

    @dp.shutdown()
    async def on_shutdown():
        logger.info("Bot is shutting down...")
        await db_manager.close_all_connections()

    # Start polling
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)
