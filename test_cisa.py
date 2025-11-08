#!/usr/bin/env python3
"""
Test CISA feed specifically to diagnose timeout issues
"""
import requests
import feedparser
import time
from datetime import datetime

CISA_URL = "https://www.cisa.gov/cybersecurity-advisories/all.xml"

print("=" * 60)
print("Testing CISA Feed")
print("=" * 60)
print(f"URL: {CISA_URL}")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test with different timeouts
for timeout in [10, 20, 30, 60]:
    print(f"--- Testing with timeout={timeout}s ---")
    start = time.time()
    
    try:
        response = requests.get(
            CISA_URL,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; NewsHackBot/1.0)'}
        )
        elapsed = time.time() - start
        
        print(f"✅ HTTP Status: {response.status_code}")
        print(f"✅ Response time: {elapsed:.2f}s")
        print(f"✅ Content length: {len(response.content)} bytes")
        
        # Try parsing
        feed = feedparser.parse(response.content)
        print(f"✅ Entries found: {len(feed.entries)}")
        
        if feed.entries:
            print(f"✅ First entry: {feed.entries[0].get('title', 'No title')[:50]}...")
        
        print(f"✅ SUCCESS with timeout={timeout}s")
        break
        
    except requests.Timeout:
        elapsed = time.time() - start
        print(f"❌ TIMEOUT after {elapsed:.2f}s")
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ ERROR after {elapsed:.2f}s: {e}")
    
    print()

print()
print("=" * 60)
print("Test completed")
print("=" * 60)
