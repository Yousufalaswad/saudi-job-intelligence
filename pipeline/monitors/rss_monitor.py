import feedparser
import requests
import os
import sys
import json
from datetime import datetime
from groq import Groq
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_client

# feedparser + requests fallback for blocked feeds
def parse_feed(url: str) -> list:
    # Try feedparser first
    feed = feedparser.parse(url)
    if feed.entries:
        return feed.entries

    # Fallback: fetch with browser headers
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return feed.entries
    except:
        pass
    return []

RSS_FEEDS = [
    {"name": "Al Yaum", "url": "https://alyaum.com/rssFeed/1005"},
    {"name": "Google News - Saudi Jobs", "url": "https://news.google.com/rss/search?q=saudi+arabia+jobs+employment&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News - Vision 2030", "url": "https://news.google.com/rss/search?q=vision+2030+saudi+jobs&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News - NEOM", "url": "https://news.google.com/rss/search?q=NEOM+jobs+workforce&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News - Saudization", "url": "https://news.google.com/rss/search?q=saudization+nitaqat+2025&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News - Saudi Labor AR", "url": "https://news.google.com/rss/search?q=وظائف+السعودية+2025&hl=ar&gl=SA&ceid=SA:ar"},
]

KEYWORDS = [
    'jobs', 'employment', 'workforce', 'hiring', 'vision 2030',
    'neom', 'saudization', 'nitaqat', 'hrdf', 'labor market',
    'gdp', 'economy', 'investment', 'sector', 'project',
    'وظائف', 'توظيف', 'نيوم', 'رؤية 2030', 'سوق العمل',
    'اقتصاد', 'استثمار', 'مشروع', 'قطاع', 'تنمية'
]

V2030_SECTOR_MAP = {
    'neom': 'NEOM',
    'نيوم': 'NEOM',
    'tourism': 'Tourism',
    'سياحة': 'Tourism',
    'hospital': 'Healthcare',
    'health': 'Healthcare',
    'صحة': 'Healthcare',
    'طبي': 'Healthcare',
    'technology': 'Technology & AI',
    'تقنية': 'Technology & AI',
    'ذكاء اصطناعي': 'Technology & AI',
    'renewable': 'Renewables',
    'solar': 'Renewables',
    'طاقة': 'Renewables',
    'aviation': 'Aviation',
    'طيران': 'Aviation',
    'mining': 'Mining',
    'تعدين': 'Mining',
    'defense': 'Defense',
    'دفاع': 'Defense',
}

def is_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw.lower() in text for kw in KEYWORDS)

def extract_v2030_update(title: str, summary: str, groq_client: Groq) -> dict:
    prompt = f"""Analyze this Saudi Arabia news article. Extract job creation targets if mentioned.

Title: {title}
Summary: {summary[:500]}

If this article mentions specific job numbers for any sector, return JSON:
{{"has_update": true, "sector": "sector name in English", "job_count": number, "confidence": 0.0-1.0}}

If no specific job numbers mentioned, return:
{{"has_update": false}}

Return only valid JSON."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=150,
        )
        content = response.choices[0].message.content.strip()
        # Clean up response
        if '```' in content:
            content = content.split('```')[1].replace('json', '').strip()
        return json.loads(content)
    except:
        return {"has_update": False}

def update_v2030_from_news(sector: str, job_count: int, source: str):
    try:
        client = get_client()
        existing = client.table("v2030_targets").select("*").eq("sector", sector).execute()
        if existing.data:
            current = existing.data[0].get("jobs_current", 0) or 0
            new_count = max(current, job_count)
            client.table("v2030_targets").update({
                "jobs_current": new_count,
                "source": source,
                "updated_at": datetime.now().isoformat()
            }).eq("sector", sector).execute()
            print(f"  Updated {sector}: {new_count:,} jobs")
    except Exception as e:
        print(f"  DB update error: {e}")

def run_rss_monitor():
    print("Starting RSS monitor...")
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    total_articles = 0
    total_relevant = 0
    total_updates = 0

    for feed_info in RSS_FEEDS:
        print(f"\nChecking {feed_info['name']}...")
        try:
            entries = parse_feed(feed_info['url'])
            total_articles += len(entries)
            print(f"  Found {len(entries)} articles")

            for entry in entries[:20]:
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))

                if not is_relevant(title, summary):
                    continue

                total_relevant += 1
                print(f"  Relevant: {title[:70]}...")

                result = extract_v2030_update(title, summary, groq_client)

                if result.get('has_update') and result.get('confidence', 0) > 0.6:
                    sector = result.get('sector', '')
                    job_count = result.get('job_count', 0)
                    if sector and job_count and job_count > 100:
                        update_v2030_from_news(sector, job_count, feed_info['name'])
                        total_updates += 1

        except Exception as e:
            print(f"  Error: {e}")
            continue

    print(f"\nDone: {total_articles} total articles, {total_relevant} relevant, {total_updates} V2030 updates")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_rss_monitor()