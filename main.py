#!/usr/bin/env python3
"""
News Hack Bot - Agregador de Notícias de Hacking e Cibersegurança
Main entry point for the bot
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import Database
from src.rss_parser import RSSParser
from src.telegram_bot import TelegramBot
from src.scheduler import FeedScheduler

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/newshack.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to run the bot"""
    logger.info("=" * 60)
    logger.info("Starting News Hack Bot")
    logger.info("=" * 60)
    
    # Get configuration from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
    db_path = os.getenv('DATABASE_PATH', './data/news.db')
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        sys.exit(1)
    
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID not set - automatic sending disabled")
    
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    # Initialize components
    logger.info("Initializing components...")
    
    try:
        # Database
        db = Database(db_path)
        logger.info("✓ Database initialized")
        
        # RSS Parser
        parser = RSSParser(timeout=30, max_retries=3)
        logger.info("✓ RSS Parser initialized")
        
        # Telegram Bot
        bot = TelegramBot(bot_token, db, parser)
        await bot.initialize()
        logger.info("✓ Telegram Bot initialized")
        
        # Scheduler
        if chat_id:
            scheduler = FeedScheduler(db, parser, bot, chat_id, check_interval)
            logger.info("✓ Scheduler initialized")
        else:
            scheduler = None
            logger.warning("⚠ Scheduler disabled (no CHAT_ID)")
        
        logger.info("=" * 60)
        logger.info("News Hack Bot is running!")
        logger.info("=" * 60)
        
        # Start polling and scheduler
        tasks = []
        
        # Start bot polling
        tasks.append(asyncio.create_task(bot.application.updater.start_polling()))
        
        # Start scheduler if enabled
        if scheduler:
            tasks.append(asyncio.create_task(scheduler.run()))
        
        # Wait for all tasks
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        if bot:
            await bot.shutdown()
        if db:
            db.close()
        logger.info("News Hack Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
