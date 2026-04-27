import asyncio
import re
from datetime import datetime
from playwright.async_api import async_playwright
from langdetect import detect
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import insert_job_posting

SAUDI_SECTORS = {
    'technology': ['software', 'developer', 'engineer', 'data', 'AI', 'cloud', 'cyber',
                   'programming', 'python', 'java', 'network', 'IT ', 'تقنية', 'برمجة', 'مطور'],
    'healthcare': ['doctor', 'nurse', 'pharmacy', 'medical', 'health', 'hospital', 'clinic',
                   'surgeon', 'dentist', 'chemist', 'chemistry', 'biology', 'lab', 'radiology',
                   'physiotherapy', 'nutrition', 'optometrist', 'veterinary', 'paramedic',
                   'طبيب', 'ممرض', 'صيدلة', 'صحة', 'مستشفى', 'أشعة', 'تغذية'],
    'finance': ['accounting', 'finance', 'audit', 'banker', 'banking', 'investment', 'tax',
                'محاسب', 'مالية', 'تدقيق', 'بنك'],
    'engineering': ['civil', 'mechanical', 'electrical', 'structural', 'construction',
                    'project manager', 'autocad', 'مهندس', 'هندسة', 'مشاريع'],
    'tourism': ['hotel', 'hospitality', 'tourism', 'chef', 'cook', 'restaurant', 'catering',
                'فندق', 'سياحة', 'ضيافة', 'طباخ'],
    'education': ['teacher', 'professor', 'instructor', 'trainer', 'tutor', 'academic',
                  'معلم', 'أستاذ', 'تدريب', 'مدرس'],
    'marketing': ['marketing', 'sales', 'brand', 'advertising', 'digital marketing', 'SEO',
                  'تسويق', 'مبيعات', 'إعلان'],
    'legal': ['lawyer', 'legal', 'attorney', 'compliance', 'محامي', 'قانون', 'امتثال'],
    'hr': ['human resources', 'HR', 'recruitment', 'talent', 'موارد بشرية', 'توظيف'],
}

VISION2030_MAP = {
    'neom': 'NEOM', 'نيوم': 'NEOM',
    'tourism': 'Tourism', 'hotel': 'Tourism', 'سياحة': 'Tourism',
    'health': 'Healthcare', 'medical': 'Healthcare', 'صحة': 'Healthcare',
    'technology': 'Technology & AI', 'AI': 'Technology & AI', 'تقنية': 'Technology & AI',
    'solar': 'Renewables', 'energy': 'Renewables', 'طاقة': 'Renewables',
    'mining': 'Mining', 'تعدين': 'Mining',
    'defense': 'Defense', 'military': 'Defense', 'دفاع': 'Defense',
    'aviation': 'Aviation', 'airline': 'Aviation', 'طيران': 'Aviation',
}

def detect_sector(title: str) -> str:
    text = title.lower()
    for sector, keywords in SAUDI_SECTORS.items():
        if any(kw.lower() in text for kw in keywords):
            return sector
    return 'other'

def detect_vision2030(title: str, company: str = "") -> str:
    text = (title + " " + company).lower()
    for keyword, sector in VISION2030_MAP.items():
        if keyword.lower() in text:
            return sector
    return None

def extract_salary(text: str):
    if not text:
        return None, None, False
    patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*[-–]\s*(\d{1,3}(?:,\d{3})*)\s*(?:SAR|sar|SR|sr)',
        r'SAR\s*(\d{1,3}(?:,\d{3})*)\s*[-–]\s*(\d{1,3}(?:,\d{3})*)',
        r'(\d{1,3}(?:,\d{3})*)\s*(?:SAR|sar|SR|sr)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return int(groups[0].replace(',', '')), int(groups[1].replace(',', '')), True
            elif len(groups) == 1:
                sal = int(groups[0].replace(',', ''))
                return sal, sal, True
    return None, None, False

async def scrape_bayt(max_pages: int = 5):
    print(f"Starting Bayt scraper — {max_pages} pages")
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"https://www.bayt.com/en/saudi-arabia/jobs/?page={page_num}"
            print(f"  Scraping page {page_num}: {url}")

            try:
                await page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await asyncio.sleep(3)

                # Fixed selector — works on all pages
                job_cards = await page.query_selector_all('li[data-job-id]')
                print(f"  Found {len(job_cards)} jobs on page {page_num}")

                if not job_cards:
                    print(f"  No jobs found on page {page_num}, stopping")
                    break

                for card in job_cards:
                    try:
                        title_el = await card.query_selector('[data-js-aid="jobID"]')
                        company_el = await card.query_selector('.t-default.t-bold')
                        location_el = await card.query_selector('.t-mute a')
                        salary_el = await card.query_selector('.jb-salary, .salary, [class*="salary"]')

                        title = await title_el.inner_text() if title_el else ""
                        company = await company_el.inner_text() if company_el else "Unknown"
                        location = await location_el.inner_text() if location_el else "Saudi Arabia"
                        salary_text = await salary_el.inner_text() if salary_el else ""

                        title = title.strip()
                        company = company.strip()
                        location = location.strip()

                        if not title:
                            continue

                        salary_min, salary_max, salary_disclosed = extract_salary(salary_text)
                        sector = detect_sector(title)
                        v2030_sector = detect_vision2030(title, company)

                        try:
                            lang = detect(title)
                            title_ar = title if lang == 'ar' else None
                            title_en = title if lang != 'ar' else None
                        except:
                            title_en = title
                            title_ar = None

                        job = {
                            "title": title_en or title,
                            "title_ar": title_ar,
                            "company": company,
                            "location": location,
                            "sector": sector,
                            "salary_min": salary_min,
                            "salary_max": salary_max,
                            "salary_disclosed": salary_disclosed,
                            "source": "bayt",
                            "posted_date": datetime.now().date().isoformat(),
                            "vision2030_sector": v2030_sector,
                            "nitaqat_relevant": sector in ['finance', 'engineering', 'healthcare', 'marketing', 'legal'],
                        }
                        jobs.append(job)

                    except Exception as e:
                        continue

                await asyncio.sleep(2)

            except Exception as e:
                print(f"  Error on page {page_num}: {e}")
                continue

        await browser.close()

    print(f"Scraped {len(jobs)} jobs total")

    saved = 0
    for job in jobs:
        try:
            insert_job_posting(job)
            saved += 1
        except Exception as e:
            continue

    print(f"Saved {saved} jobs to database")
    return jobs

if __name__ == "__main__":
    asyncio.run(scrape_bayt(max_pages=5))