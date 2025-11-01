#!/usr/bin/env python3
"""
Test script to verify RSS feeds are working
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.rss_parser import RSSParser
from config.rss_feeds import get_all_feeds, get_high_priority_feeds

def test_single_feed(parser, feed):
    """Test a single feed"""
    print(f"\n{'='*60}")
    print(f"Testing: {feed['name']}")
    print(f"URL: {feed['url']}")
    print(f"Category: {feed['category']} | Priority: {feed['priority']}")
    print(f"{'='*60}")
    
    result = parser.test_feed(feed['url'])
    
    if result['success']:
        print(f"✅ SUCCESS - Found {result['entries_count']} entries")
    else:
        print(f"❌ FAILED - {result['error']}")
    
    return result['success']

def main():
    print("🔐 News Hack Bot - Feed Tester")
    print("="*60)
    
    parser = RSSParser(timeout=15, max_retries=2)
    
    # Test high priority feeds first
    print("\n📡 Testing HIGH PRIORITY feeds...")
    high_priority = get_high_priority_feeds()
    
    success_count = 0
    fail_count = 0
    
    for feed in high_priority[:10]:  # Test first 10
        if test_single_feed(parser, feed):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Results:")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📈 Success Rate: {(success_count/(success_count+fail_count)*100):.1f}%")
    print(f"{'='*60}")
    
    if fail_count > 0:
        print("\n⚠️  Some feeds failed. This is normal - some feeds may be temporarily down.")
        print("The bot will skip failed feeds and continue with working ones.")
    
    print("\n✅ Feed test completed!")

if __name__ == "__main__":
    main()
