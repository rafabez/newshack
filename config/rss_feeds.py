"""
RSS Feeds Configuration
Curated list of cybersecurity, hacking, and infosec news sources
"""

RSS_FEEDS = {
    # === MAINSTREAM CYBERSECURITY NEWS ===
    "mainstream": [
        {
            "name": "The Hacker News",
            "url": "https://feeds.feedburner.com/TheHackersNews",
            "category": "news",
            "priority": "high"
        },
        {
            "name": "Krebs on Security",
            "url": "https://krebsonsecurity.com/feed/",
            "category": "news",
            "priority": "high"
        },
        {
            "name": "Bleeping Computer",
            "url": "https://www.bleepingcomputer.com/feed/",
            "category": "news",
            "priority": "high"
        },
        {
            "name": "Dark Reading",
            "url": "https://www.darkreading.com/rss.xml",
            "category": "news",
            "priority": "high"
        },
        {
            "name": "Threatpost",
            "url": "https://threatpost.com/feed/",
            "category": "news",
            "priority": "high"
        },
        {
            "name": "Security Affairs",
            "url": "https://securityaffairs.co/wordpress/feed",
            "category": "news",
            "priority": "high"
        },
        {
            "name": "Schneier on Security",
            "url": "https://www.schneier.com/feed/atom",
            "category": "analysis",
            "priority": "high"
        },
        {
            "name": "Graham Cluley",
            "url": "https://grahamcluley.com/feed/",
            "category": "news",
            "priority": "medium"
        },
        {
            "name": "Troy Hunt",
            "url": "https://www.troyhunt.com/rss/",
            "category": "analysis",
            "priority": "high"
        },
        {
            "name": "Infosecurity Magazine",
            "url": "https://www.infosecurity-magazine.com/rss/news/",
            "category": "news",
            "priority": "medium"
        },
    ],
    
    # === THREAT INTELLIGENCE & RESEARCH ===
    "threat_intel": [
        {
            "name": "Google Project Zero",
            "url": "https://googleprojectzero.blogspot.com/feeds/posts/default",
            "category": "research",
            "priority": "high"
        },
        {
            "name": "Cisco Talos",
            "url": "https://blog.talosintelligence.com/rss/",
            "category": "threat_intel",
            "priority": "high"
        },
        {
            "name": "Kaspersky Securelist",
            "url": "https://securelist.com/feed/",
            "category": "threat_intel",
            "priority": "high"
        },
        {
            "name": "Mandiant",
            "url": "https://www.mandiant.com/resources/blog/rss.xml",
            "category": "threat_intel",
            "priority": "high"
        },
        {
            "name": "CrowdStrike Blog",
            "url": "https://www.crowdstrike.com/blog/feed/",
            "category": "threat_intel",
            "priority": "high"
        },
        {
            "name": "Palo Alto Unit 42",
            "url": "https://unit42.paloaltonetworks.com/feed/",
            "category": "threat_intel",
            "priority": "high"
        },
        {
            "name": "Trend Micro Research",
            "url": "https://www.trendmicro.com/en_us/research.rss",
            "category": "threat_intel",
            "priority": "medium"
        },
        {
            "name": "Checkpoint Research",
            "url": "https://research.checkpoint.com/feed/",
            "category": "research",
            "priority": "high"
        },
        {
            "name": "ESET Research",
            "url": "https://www.welivesecurity.com/en/rss/feed/",
            "category": "research",
            "priority": "medium"
        },
        {
            "name": "Bitdefender Labs",
            "url": "https://www.bitdefender.com/blog/api/rss/labs/",
            "category": "research",
            "priority": "medium"
        },
    ],
    
    # === VULNERABILITY DISCLOSURE & EXPLOITS ===
    "vulnerabilities": [
        {
            "name": "Exploit-DB",
            "url": "https://www.exploit-db.com/rss.xml",
            "category": "exploits",
            "priority": "high"
        },
        {
            "name": "Zero Day Initiative",
            "url": "https://www.zerodayinitiative.com/rss/published/",
            "category": "vulnerabilities",
            "priority": "high"
        },
        {
            "name": "Packet Storm Security",
            "url": "https://packetstormsecurity.com/feeds/news/",
            "category": "exploits",
            "priority": "high"
        },
        {
            "name": "CISA Advisories",
            "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
            "category": "advisories",
            "priority": "medium"
        },
    ],
    
    # === UNDERGROUND & INDEPENDENT BLOGS ===
    "underground": [
        {
            "name": "Darknet - Hacking Tools",
            "url": "https://www.darknet.org.uk/feed/",
            "category": "tools",
            "priority": "high"
        },
        {
            "name": "Hacker Combat",
            "url": "https://www.hackercombat.com/feed/",
            "category": "tutorials",
            "priority": "medium"
        },
        {
            "name": "Null Byte",
            "url": "https://null-byte.wonderhowto.com/rss.xml",
            "category": "tutorials",
            "priority": "high"
        },
        {
            "name": "SecJuice",
            "url": "https://www.secjuice.com/feed/",
            "category": "tools",
            "priority": "high"
        },
        {
            "name": "PentestMonkey",
            "url": "http://pentestmonkey.net/feed",
            "category": "tools",
            "priority": "high"
        },
        {
            "name": "GitHub Security Lab",
            "url": "https://securitylab.github.com/research/feed.xml",
            "category": "research",
            "priority": "high"
        },
        {
            "name": "InfoSec Write-ups",
            "url": "https://infosecwriteups.com/feed",
            "category": "tutorials",
            "priority": "high"
        },
        {
            "name": "Social-Engineer.org",
            "url": "https://www.social-engineer.org/feed/",
            "category": "tools",
            "priority": "medium"
        },
        {
            "name": "ZSec UK Blog",
            "url": "https://blog.zsec.uk/feed/",
            "category": "tools",
            "priority": "medium"
        },
        {
            "name": "Hakin9",
            "url": "https://hakin9.org/feed/",
            "category": "tools",
            "priority": "medium"
        },
        {
            "name": "Pentest Geek",
            "url": "https://www.pentestgeek.com/feed/",
            "category": "pentest",
            "priority": "medium"
        },
        {
            "name": "PortSwigger Research",
            "url": "https://portswigger.net/research/rss",
            "category": "research",
            "priority": "high"
        },
        {
            "name": "Bishop Fox Blog",
            "url": "https://bishopfox.com/feeds/blog.rss",
            "category": "pentest",
            "priority": "medium"
        },
        {
            "name": "Offensive Security Blog",
            "url": "https://www.offensive-security.com/blog/feed/",
            "category": "pentest",
            "priority": "medium"
        },
        {
            "name": "Rapid7 Blog",
            "url": "https://blog.rapid7.com/rss/",
            "category": "research",
            "priority": "medium"
        },
        {
            "name": "Praetorian Blog",
            "url": "https://www.praetorian.com/blog/feed/",
            "category": "research",
            "priority": "medium"
        },
    ],
    
    # === TECHNICAL RESEARCH & REVERSE ENGINEERING ===
    "technical": [
        {
            "name": "Trail of Bits Blog",
            "url": "https://blog.trailofbits.com/feed/",
            "category": "research",
            "priority": "high"
        },
        {
            "name": "NCC Group Research",
            "url": "https://research.nccgroup.com/feed/",
            "category": "research",
            "priority": "high"
        },
        {
            "name": "Quarkslab Blog",
            "url": "https://blog.quarkslab.com/feeds/all.rss.xml",
            "category": "research",
            "priority": "medium"
        },
        {
            "name": "Positive Security",
            "url": "https://positive.security/blog/rss.xml",
            "category": "research",
            "priority": "medium"
        },
        {
            "name": "RCE Security",
            "url": "https://www.rcesecurity.com/feed",
            "category": "exploits",
            "priority": "medium"
        },
        {
            "name": "Cryptography Engineering",
            "url": "https://blog.cryptographyengineering.com/feed",
            "category": "crypto",
            "priority": "medium"
        },
    ],
    
    # === REDDIT & COMMUNITY ===
    "community": [
        {
            "name": "r/netsec",
            "url": "https://www.reddit.com/r/netsec/.rss",
            "category": "community",
            "priority": "medium"
        },
        {
            "name": "r/blackhat",
            "url": "https://www.reddit.com/r/blackhat/.rss",
            "category": "community",
            "priority": "medium"
        },
        {
            "name": "r/ReverseEngineering",
            "url": "https://www.reddit.com/r/ReverseEngineering/.rss",
            "category": "community",
            "priority": "low"
        },
    ],
    
    # === MALWARE ANALYSIS ===
    "malware": [
        {
            "name": "Malwarebytes Labs",
            "url": "https://www.malwarebytes.com/blog/feed",
            "category": "malware",
            "priority": "high"
        },
        {
            "name": "ANY.RUN Blog",
            "url": "https://any.run/cybersecurity-blog/feed/",
            "category": "malware",
            "priority": "high"
        },
        {
            "name": "Avast Decoded",
            "url": "https://decoded.avast.io/feed/",
            "category": "malware",
            "priority": "high"
        },
        {
            "name": "The DFIR Report",
            "url": "https://thedfirreport.com/feed/",
            "category": "malware",
            "priority": "high"
        },
        {
            "name": "Hybrid Analysis Blog",
            "url": "https://www.hybrid-analysis.com/feed",
            "category": "malware",
            "priority": "high"
        },
    ],
    
    # === CLOUD & DEVOPS SECURITY ===
    "cloud": [
        {
            "name": "AWS Security Blog",
            "url": "https://aws.amazon.com/blogs/security/feed/",
            "category": "cloud",
            "priority": "medium"
        },
        {
            "name": "Google Cloud Security",
            "url": "https://cloud.google.com/blog/products/identity-security/rss",
            "category": "cloud",
            "priority": "medium"
        },
        {
            "name": "Microsoft Security",
            "url": "https://www.microsoft.com/en-us/security/blog/feed/",
            "category": "cloud",
            "priority": "medium"
        },
    ],
}

def get_all_feeds():
    """Return all RSS feeds as a flat list"""
    all_feeds = []
    for category_feeds in RSS_FEEDS.values():
        all_feeds.extend(category_feeds)
    return all_feeds

def get_feeds_by_category(category):
    """Get feeds by category group"""
    return RSS_FEEDS.get(category, [])

def get_high_priority_feeds():
    """Get only high priority feeds"""
    high_priority = []
    for category_feeds in RSS_FEEDS.values():
        high_priority.extend([f for f in category_feeds if f.get("priority") == "high"])
    return high_priority
