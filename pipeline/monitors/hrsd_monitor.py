import requests
import os
import sys
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from pypdf import PdfReader
from io import BytesIO
from groq import Groq
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import upsert_nitaqat_rule

HRSD_URLS = [
    "https://www.hrsd.gov.sa/en/media-center/news",
    "https://www.hrdf.org.sa/en/media-center/news",
]

NITAQAT_KEYWORDS = [
    'saudization', 'nitaqat', 'localization', 'quota', 'percentage',
    'توطين', 'نطاقات', 'سعودة', 'نسبة', 'مهنة', 'profession'
]

def fetch_page(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5,ar;q=0.3',
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
    return ""

def extract_pdf_text(pdf_url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(pdf_url, headers=headers, timeout=20)
        if response.status_code == 200:
            pdf_file = BytesIO(response.content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages[:5]:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        print(f"  PDF error: {e}")
    return ""

def extract_nitaqat_rules(text: str, source_url: str, groq_client: Groq) -> list:
    if len(text) > 3000:
        text = text[:3000]

    prompt = f"""Analyze this Saudi Arabian government text about Saudization/Nitaqat regulations.

Text: {text}

Extract any Saudization quota rules mentioned. For each rule found, return a JSON array:
[
  {{
    "profession": "profession name in English",
    "profession_ar": "profession name in Arabic if available",
    "current_quota": percentage as number (e.g. 40),
    "target_quota": target percentage as number,
    "deadline": "YYYY-MM-DD if mentioned, else null",
    "min_salary": minimum salary in SAR as number or 0,
    "sector": "sector name",
    "confidence": 0.0-1.0
  }}
]

If no specific quota rules are found, return an empty array: []
Return only valid JSON, no explanation."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()
        if '```' in content:
            content = content.split('```')[1].replace('json', '').strip()
        rules = json.loads(content)
        if isinstance(rules, list):
            return rules
    except Exception as e:
        pass
    return []

def is_nitaqat_relevant(text: str) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in NITAQAT_KEYWORDS)

def run_hrsd_monitor():
    print("Starting HRSD monitor...")
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    total_pages = 0
    total_pdfs = 0
    total_rules = 0

    for base_url in HRSD_URLS:
        print(f"\nChecking {base_url}...")
        html = fetch_page(base_url)
        if not html:
            print(f"  Could not fetch page")
            continue

        soup = BeautifulSoup(html, 'html.parser')
        total_pages += 1

        # Find news links
        links = soup.find_all('a', href=True)
        news_links = []
        for link in links:
            href = link['href']
            text = link.get_text(strip=True)
            if is_nitaqat_relevant(text) or is_nitaqat_relevant(href):
                full_url = href if href.startswith('http') else base_url.rstrip('/news') + href
                news_links.append(full_url)

        print(f"  Found {len(news_links)} relevant links")

        # Find PDF links
        pdf_links = []
        for link in links:
            href = link['href']
            if href.endswith('.pdf') or '/pdf/' in href.lower():
                full_url = href if href.startswith('http') else base_url.rstrip('/news') + href
                pdf_links.append(full_url)

        print(f"  Found {len(pdf_links)} PDF links")

        # Process page text directly
        page_text = soup.get_text(separator=' ', strip=True)
        if is_nitaqat_relevant(page_text):
            print(f"  Extracting rules from page text...")
            rules = extract_nitaqat_rules(page_text, base_url, groq_client)
            for rule in rules:
                if rule.get('confidence', 0) > 0.7 and rule.get('profession'):
                    try:
                        upsert_nitaqat_rule({
                            "profession": rule['profession'],
                            "profession_ar": rule.get('profession_ar'),
                            "current_quota": rule.get('current_quota', 0),
                            "target_quota": rule.get('target_quota', rule.get('current_quota', 0)),
                            "deadline": rule.get('deadline'),
                            "min_salary": rule.get('min_salary', 0),
                            "sector": rule.get('sector', 'Unknown'),
                            "source_url": base_url,
                            "confidence": rule.get('confidence', 0.8),
                            "extracted_at": datetime.now().isoformat(),
                        })
                        print(f"  Saved rule: {rule['profession']} — {rule.get('current_quota')}%")
                        total_rules += 1
                    except Exception as e:
                        print(f"  Save error: {e}")

        # Process PDFs
        for pdf_url in pdf_links[:3]:
            print(f"  Reading PDF: {pdf_url[:60]}...")
            pdf_text = extract_pdf_text(pdf_url)
            if pdf_text and is_nitaqat_relevant(pdf_text):
                total_pdfs += 1
                rules = extract_nitaqat_rules(pdf_text, pdf_url, groq_client)
                for rule in rules:
                    if rule.get('confidence', 0) > 0.7 and rule.get('profession'):
                        try:
                            upsert_nitaqat_rule({
                                "profession": rule['profession'],
                                "profession_ar": rule.get('profession_ar'),
                                "current_quota": rule.get('current_quota', 0),
                                "target_quota": rule.get('target_quota', rule.get('current_quota', 0)),
                                "deadline": rule.get('deadline'),
                                "min_salary": rule.get('min_salary', 0),
                                "sector": rule.get('sector', 'Unknown'),
                                "source_url": pdf_url,
                                "confidence": rule.get('confidence', 0.8),
                                "extracted_at": datetime.now().isoformat(),
                            })
                            print(f"  Saved PDF rule: {rule['profession']} — {rule.get('current_quota')}%")
                            total_rules += 1
                        except Exception as e:
                            print(f"  Save error: {e}")

    print(f"\nHRSD monitor done: {total_pages} pages, {total_pdfs} PDFs, {total_rules} rules extracted")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_hrsd_monitor()