"""
Database module for storing and managing RSS feed entries
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class Database:
    """SQLite database handler for news entries"""
    
    def __init__(self, db_path: str = "./data/news.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self._ensure_data_dir()
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # News entries table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS news_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_name TEXT NOT NULL,
                    feed_url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT UNIQUE NOT NULL,
                    description TEXT,
                    published_date TEXT,
                    category TEXT,
                    priority TEXT,
                    image_url TEXT,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_to_telegram BOOLEAN DEFAULT 0,
                    sent_at TIMESTAMP
                )
            """)
            
            # Add image_url column if it doesn't exist (migration)
            try:
                self.cursor.execute("ALTER TABLE news_entries ADD COLUMN image_url TEXT")
                logger.info("Added image_url column to news_entries table")
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            # Feed status table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS feed_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_name TEXT UNIQUE NOT NULL,
                    feed_url TEXT NOT NULL,
                    last_checked TIMESTAMP,
                    last_success TIMESTAMP,
                    error_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create indexes for better performance
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_link ON news_entries(link)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sent ON news_entries(sent_to_telegram)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_published ON news_entries(published_date DESC)
            """)
            
            self.conn.commit()
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def add_news_entry(self, entry: Dict) -> bool:
        """
        Add a news entry to database
        Returns True if added, False if duplicate
        """
        try:
            self.cursor.execute("""
                INSERT INTO news_entries 
                (feed_name, feed_url, title, link, description, published_date, category, priority, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.get('feed_name'),
                entry.get('feed_url'),
                entry.get('title'),
                entry.get('link'),
                entry.get('description'),
                entry.get('published_date'),
                entry.get('category'),
                entry.get('priority'),
                entry.get('image_url')
            ))
            self.conn.commit()
            logger.debug(f"Added news entry: {entry.get('title')[:50]}...")
            return True
        except sqlite3.IntegrityError:
            # Duplicate entry
            return False
        except Exception as e:
            logger.error(f"Error adding news entry: {e}")
            return False
    
    def get_unsent_news(self, limit: Optional[int] = None) -> List[Dict]:
        """Get news entries that haven't been sent to Telegram"""
        try:
            query = """
                SELECT * FROM news_entries 
                WHERE sent_to_telegram = 0 
                ORDER BY published_date DESC, fetched_at DESC
            """
            if limit:
                query += f" LIMIT {limit}"
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting unsent news: {e}")
            return []
    
    def mark_as_sent(self, entry_id: int) -> bool:
        """Mark a news entry as sent to Telegram"""
        try:
            self.cursor.execute("""
                UPDATE news_entries 
                SET sent_to_telegram = 1, sent_at = ? 
                WHERE id = ?
            """, (datetime.now().isoformat(), entry_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error marking entry as sent: {e}")
            return False
    
    def get_recent_news(self, hours: int = 24, limit: int = 20) -> List[Dict]:
        """Get recent news from last N hours"""
        try:
            self.cursor.execute("""
                SELECT * FROM news_entries 
                WHERE datetime(fetched_at) > datetime('now', '-' || ? || ' hours')
                ORDER BY published_date DESC, fetched_at DESC
                LIMIT ?
            """, (hours, limit))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting recent news: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {}
            
            # Total entries
            self.cursor.execute("SELECT COUNT(*) as count FROM news_entries")
            stats['total_entries'] = self.cursor.fetchone()['count']
            
            # Sent entries
            self.cursor.execute("SELECT COUNT(*) as count FROM news_entries WHERE sent_to_telegram = 1")
            stats['sent_entries'] = self.cursor.fetchone()['count']
            
            # Unsent entries
            self.cursor.execute("SELECT COUNT(*) as count FROM news_entries WHERE sent_to_telegram = 0")
            stats['unsent_entries'] = self.cursor.fetchone()['count']
            
            # Entries today
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM news_entries 
                WHERE date(fetched_at) = date('now')
            """)
            stats['today_entries'] = self.cursor.fetchone()['count']
            
            # Entries by category
            self.cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM news_entries 
                GROUP BY category 
                ORDER BY count DESC
            """)
            stats['by_category'] = {row['category']: row['count'] for row in self.cursor.fetchall()}
            
            return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def update_feed_status(self, feed_name: str, feed_url: str, success: bool = True, error: str = None):
        """Update feed check status"""
        try:
            now = datetime.now().isoformat()
            
            if success:
                self.cursor.execute("""
                    INSERT INTO feed_status (feed_name, feed_url, last_checked, last_success, error_count)
                    VALUES (?, ?, ?, ?, 0)
                    ON CONFLICT(feed_name) DO UPDATE SET
                        last_checked = ?,
                        last_success = ?,
                        error_count = 0,
                        last_error = NULL
                """, (feed_name, feed_url, now, now, now, now))
            else:
                self.cursor.execute("""
                    INSERT INTO feed_status (feed_name, feed_url, last_checked, error_count, last_error)
                    VALUES (?, ?, ?, 1, ?)
                    ON CONFLICT(feed_name) DO UPDATE SET
                        last_checked = ?,
                        error_count = error_count + 1,
                        last_error = ?
                """, (feed_name, feed_url, now, error, now, error))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error updating feed status: {e}")
    
    def get_feed_status(self) -> List[Dict]:
        """Get status of all feeds"""
        try:
            self.cursor.execute("""
                SELECT * FROM feed_status 
                ORDER BY last_checked DESC
            """)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting feed status: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
