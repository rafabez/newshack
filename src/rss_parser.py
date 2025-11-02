"""
RSS Feed Parser module
Fetches and parses RSS feeds from various cybersecurity sources
"""
import feedparser
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)


class RSSParser:
    """RSS Feed Parser with error handling and retry logic"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize RSS Parser
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def parse_feed(self, feed_config: Dict) -> List[Dict]:
        """
        Parse a single RSS feed
        
        Args:
            feed_config: Dictionary with feed configuration (name, url, category, priority)
        
        Returns:
            List of parsed entries
        """
        feed_name = feed_config.get('name', 'Unknown')
        feed_url = feed_config.get('url')
        
        if not feed_url:
            logger.error(f"No URL provided for feed: {feed_name}")
            return []
        
        logger.info(f"Parsing feed: {feed_name}")
        
        for attempt in range(self.max_retries):
            try:
                # Fetch feed with timeout to prevent hanging
                logger.debug(f"Fetching feed: {feed_url} (timeout: {self.timeout}s)")
                response = self.session.get(feed_url, timeout=self.timeout)
                response.raise_for_status()
                
                # Parse the feed from content
                feed = feedparser.parse(response.content)
                
                if feed.bozo:
                    logger.warning(f"Feed parsing warning for {feed_name}: {feed.bozo_exception}")
                
                if not feed.entries:
                    logger.warning(f"No entries found in feed: {feed_name}")
                    return []
                
                # Process entries
                entries = []
                for entry in feed.entries:
                    parsed_entry = self._parse_entry(entry, feed_config)
                    if parsed_entry:
                        entries.append(parsed_entry)
                
                logger.info(f"Successfully parsed {len(entries)} entries from {feed_name}")
                return entries
                
            except requests.Timeout:
                logger.error(f"Timeout fetching feed {feed_name} after {self.timeout}s (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return []
            except Exception as e:
                logger.error(f"Error parsing feed {feed_name} (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return []
        
        return []
    
    def _parse_entry(self, entry, feed_config: Dict) -> Optional[Dict]:
        """
        Parse a single feed entry
        
        Args:
            entry: feedparser entry object
            feed_config: Feed configuration dictionary
        
        Returns:
            Parsed entry dictionary or None
        """
        try:
            # Extract title
            title = entry.get('title', 'No Title').strip()
            
            # Extract link
            link = entry.get('link', '')
            if not link:
                logger.warning(f"Entry without link in {feed_config.get('name')}")
                return None
            
            # Extract description/summary
            description = entry.get('summary', entry.get('description', ''))
            if description:
                description = self._clean_html(description)
            
            # Extract published date
            published_date = self._parse_date(entry)
            
            # Extract image/thumbnail
            image_url = None
            
            # Try media:thumbnail
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get('url')
            
            # Try enclosure (common in RSS)
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        image_url = enclosure.get('href') or enclosure.get('url')
                        break
            
            # Try media:content
            elif hasattr(entry, 'media_content') and entry.media_content:
                for media in entry.media_content:
                    if media.get('medium') == 'image' or media.get('type', '').startswith('image/'):
                        image_url = media.get('url')
                        break
            
            # Try extracting from description HTML (last resort)
            if not image_url and description:
                try:
                    soup = BeautifulSoup(entry.get('summary', entry.get('description', '')), 'lxml')
                    img_tag = soup.find('img')
                    if img_tag and img_tag.get('src'):
                        image_url = img_tag['src']
                        # Ensure it's a full URL
                        if image_url and not image_url.startswith(('http://', 'https://')):
                            image_url = None
                except:
                    pass
            
            # Build entry dictionary
            parsed_entry = {
                'feed_name': feed_config.get('name'),
                'feed_url': feed_config.get('url'),
                'title': title,
                'link': link,
                'description': description[:500] if description else '',  # Limit description length
                'published_date': published_date,
                'category': feed_config.get('category', 'general'),
                'priority': feed_config.get('priority', 'medium'),
                'image_url': image_url
            }
            
            return parsed_entry
            
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None
    
    def _clean_html(self, html_text: str) -> str:
        """
        Clean HTML tags from text
        
        Args:
            html_text: HTML string
        
        Returns:
            Cleaned text
        """
        try:
            soup = BeautifulSoup(html_text, 'lxml')
            text = soup.get_text(separator=' ', strip=True)
            # Remove extra whitespace
            text = ' '.join(text.split())
            return text
        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html_text
    
    def _parse_date(self, entry) -> str:
        """
        Parse and normalize date from entry
        
        Args:
            entry: feedparser entry object
        
        Returns:
            ISO format date string
        """
        try:
            # Try different date fields
            date_tuple = entry.get('published_parsed') or entry.get('updated_parsed')
            
            if date_tuple:
                dt = datetime(*date_tuple[:6])
                return dt.isoformat()
            
            # Fallback to current time
            return datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            return datetime.now().isoformat()
    
    def parse_multiple_feeds(self, feeds: List[Dict], delay: float = 1.0) -> List[Dict]:
        """
        Parse multiple RSS feeds with delay between requests
        
        Args:
            feeds: List of feed configurations
            delay: Delay between requests in seconds
        
        Returns:
            List of all parsed entries
        """
        all_entries = []
        
        for i, feed_config in enumerate(feeds):
            entries = self.parse_feed(feed_config)
            all_entries.extend(entries)
            
            # Add delay between requests (except for last feed)
            if i < len(feeds) - 1 and delay > 0:
                time.sleep(delay)
        
        logger.info(f"Total entries parsed from {len(feeds)} feeds: {len(all_entries)}")
        return all_entries
    
    def test_feed(self, feed_url: str) -> Dict:
        """
        Test a single feed URL
        
        Args:
            feed_url: RSS feed URL
        
        Returns:
            Dictionary with test results
        """
        result = {
            'url': feed_url,
            'success': False,
            'entries_count': 0,
            'error': None
        }
        
        try:
            feed = feedparser.parse(feed_url, request_headers=dict(self.session.headers))
            
            if feed.bozo:
                result['error'] = str(feed.bozo_exception)
            
            result['entries_count'] = len(feed.entries)
            result['success'] = len(feed.entries) > 0
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
