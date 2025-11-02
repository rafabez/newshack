"""
Scheduler module for automatic RSS feed checking
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
import schedule
import time

logger = logging.getLogger(__name__)


class FeedScheduler:
    """Scheduler for automatic RSS feed updates"""
    
    def __init__(self, database, rss_parser, telegram_bot, chat_id: str, check_interval: int = 30):
        """
        Initialize Feed Scheduler
        
        Args:
            database: Database instance
            rss_parser: RSS Parser instance
            telegram_bot: Telegram Bot instance
            chat_id: Telegram chat ID to send news to
            check_interval: Check interval in minutes
        """
        self.db = database
        self.parser = rss_parser
        self.bot = telegram_bot
        self.chat_id = chat_id
        self.check_interval = check_interval
        self.is_running = False
        self.last_check = None
    
    async def check_feeds(self):
        """Check all RSS feeds for new entries"""
        logger.info("Starting scheduled feed check...")
        self.last_check = datetime.now()
        
        from config.rss_feeds import get_all_feeds
        feeds = get_all_feeds()
        
        total_new = 0
        
        # Parse all feeds and collect new entries (don't send immediately)
        for feed in feeds:
            try:
                entries = self.parser.parse_feed(feed)
                
                for entry in entries:
                    if self.db.add_news_entry(entry):
                        total_new += 1
                
                self.db.update_feed_status(feed['name'], feed['url'], success=True)
                
                # Small delay between feeds
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error checking feed {feed.get('name')}: {e}")
                self.db.update_feed_status(feed['name'], feed['url'], success=False, error=str(e))
        
        # Now send unsent news in controlled batches
        total_sent = 0
        if total_new > 0:
            # Get all unsent news (limited to avoid spam)
            unsent = self.db.get_unsent_news(limit=20)  # Max 20 per check cycle
            if unsent:
                logger.info(f"Sending {len(unsent)} new entries to Telegram...")
                sent = await self.bot.send_news_to_channel(self.chat_id, unsent)
                total_sent = sent
        
        logger.info(f"Feed check completed: {total_new} new entries found, {total_sent} sent to Telegram")
        
        return total_new, total_sent
    
    async def initial_load(self):
        """Load initial news on bot startup"""
        logger.info("Loading initial news...")
        
        from config.rss_feeds import get_high_priority_feeds
        feeds = get_high_priority_feeds()
        
        total_loaded = 0
        
        # Parse high priority feeds (increased to include all tools/malware feeds)
        for feed in feeds[:35]:  # Limit initial load to top 35 high priority feeds
            try:
                entries = self.parser.parse_feed(feed)
                
                for entry in entries[:5]:  # Limit entries per feed
                    if self.db.add_news_entry(entry):
                        total_loaded += 1
                
                self.db.update_feed_status(feed['name'], feed['url'], success=True)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in initial load for {feed.get('name')}: {e}")
                self.db.update_feed_status(feed['name'], feed['url'], success=False, error=str(e))
        
        logger.info(f"Initial load completed: {total_loaded} entries loaded")
        
        # Send ONLY a small welcome batch (5 entries) to avoid spam
        # The rest will be sent gradually by scheduled checks
        unsent = self.db.get_unsent_news(limit=5)
        if unsent:
            sent = await self.bot.send_news_to_channel(self.chat_id, unsent)
            logger.info(f"Sent {sent} initial news to Telegram (welcome batch)")
        
        return total_loaded
    
    async def run(self):
        """Run the scheduler loop"""
        self.is_running = True
        logger.info("Scheduler started")
        
        # Initial load
        await self.initial_load()
        
        logger.info(f"Scheduled feed checks every {self.check_interval} minutes")
        
        # Run scheduler loop with asyncio (more reliable than schedule library)
        while self.is_running:
            try:
                # Wait for the check interval
                await asyncio.sleep(self.check_interval * 60)
                
                # Run feed check
                if self.is_running:
                    await self.check_feeds()
                    
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                # Continue running even if there's an error
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        logger.info("Scheduler stopped")
