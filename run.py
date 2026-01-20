import asyncio
import logging
from telesonar.config import TELEGRAM_BOT_TOKEN, PERPLEXITY_API_KEY
from telesonar.bot import TeleSonarBot

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    if not TELEGRAM_BOT_TOKEN or not PERPLEXITY_API_KEY:
        logger.error("❌ Error: TELEGRAM_BOT_TOKEN and PERPLEXITY_API_KEY must be set in .env file.")
        return

    logger.info("🚀 Bot is starting...")
    
    bot_instance = TeleSonarBot()
    
    try:
        await bot_instance.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await bot_instance.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
