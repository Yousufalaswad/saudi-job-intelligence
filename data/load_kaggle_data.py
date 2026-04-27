import pandas as pd
import os
import sys
from datetime import datetime
from langdetect import detect
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import insert_job_posting

SECTOR_MAP = {
    'تقنية المعلومات': 'Technology',
    'الرعاية الصحية': 'Healthcare',
    'التعليم': 'Education',
    'المالية': 'Finance',
    'الهندسة': 'Engineering',
    'التسويق': 'Marketing',
    'المبيعات': 'Marketing',
    'الموارد البشرية': 'HR',
    'القانون': 'Legal',
    'السياحة': 'Tourism',
    'الطاقة': 'Renewables',
    'التصنيع': 'Engineering',
    'البناء': 'Engineering',
    'النقل': 'Engineering',
    'الاتصالات': 'Technology',
}

VISION2030_MAP = {
    'تقنية': 'Technology & AI',
    'technology': 'Technology & AI',
    'software': 'Technology & AI',
    'data': 'Technology & AI',
    'ai': 'Technology & AI',
    'health': 'Healthcare',
    'medical': 'Healthcare',
    'hospital': 'Healthcare',
    'صحة': 'Healthcare',
    'tourism': 'Tourism',
    'hotel': 'Tourism',
    'سياحة': 'Tourism',
    'neom': 'NEOM',
    'نيوم': 'NEOM',
    'energy': 'Renewables',
    'solar': 'Renewables',
    'طاقة': 'Renewables',
    'mining': 'Mining',
    'تعدين': 'Mining',
    'defense': 'Defense',
    'military': 'Defense',
    'aviation': 'Aviation',
    'airline': 'Aviation',
    'طيران': 'Aviation',
}

def detect_sector(text: str) -> str:
    if not text:
        return 'other'
    for arabic, english in SECTOR_MAP.items():
        if arabic in str(text):
            return english.lower()
    text_lower = str(text).lower()
    if any(k in text_lower for k in ['software', 'data', 'tech', 'it ', 'cyber', 'cloud']):
        return 'technology'
    if any(k in text_lower for k in ['doctor', 'nurse', 'medical', 'health', 'pharma']):
        return 'healthcare'
    if any(k in text_lower for k in ['engineer', 'civil', 'mechanical', 'electrical']):
        return 'engineering'
    if any(k in text_lower for k in ['account', 'finance', 'audit', 'banking']):
        return 'finance'
    if any(k in text_lower for k in ['market', 'sales', 'brand']):
        return 'marketing'
    if any(k in text_lower for k in ['teach', 'professor', 'education', 'training']):
        return 'education'
    return 'other'

def detect_v2030(text: str) -> str:
    if not text:
        return None
    text_lower = str(text).lower()
    for keyword, sector in VISION2030_MAP.items():
        if keyword.lower() in text_lower:
            return sector
    return None

def parse_salary(salary_str) -> tuple:
    if pd.isna(salary_str) or salary_str == '' or salary_str == 'غير محدد':
        return None, None, False
    try:
        salary_str = str(salary_str).replace(',', '').replace('SAR', '').replace('ريال', '').strip()
        if '-' in salary_str:
            parts = salary_str.split('-')
            return int(float(parts[0].strip())), int(float(parts[1].strip())), True
        val = int(float(salary_str))
        if val > 0:
            return val, val, True
    except:
        pass
    return None, None, False

def load_jadarat(path: str) -> int:
    print(f"Loading Jadarat dataset from {path}...")
    try:
        df = pd.read_csv(path, encoding='utf-8')
    except:
        df = pd.read_csv(path, encoding='latin-1')

    print(f"  Found {len(df)} rows")
    saved = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            title = str(row.get('job_title', '')).strip()
            if not title or title == 'nan':
                skipped += 1
                continue

            company = str(row.get('comp_name', 'Unknown')).strip()
            region = str(row.get('region', 'Saudi Arabia')).strip()
            city = str(row.get('city', '')).strip()
            location = f"{city}, {region}" if city and city != 'nan' else region
            eco_activity = str(row.get('eco_activity', '')).strip()
            salary_raw = row.get('Salary', '')
            salary_min, salary_max, salary_disclosed = parse_salary(salary_raw)
            sector = detect_sector(eco_activity or title)
            v2030 = detect_v2030(title + ' ' + eco_activity)

            try:
                lang = detect(title)
                title_ar = title if lang == 'ar' else None
                title_en = title if lang != 'ar' else None
            except:
                title_en = title
                title_ar = None

            job_date = str(row.get('job_date', '')).strip()
            try:
                posted_date = pd.to_datetime(job_date).date().isoformat()
            except:
                posted_date = datetime.now().date().isoformat()

            posting = {
                "title": title_en or title,
                "title_ar": title_ar,
                "company": company if company != 'nan' else 'Unknown',
                "location": location if location != 'nan' else 'Saudi Arabia',
                "sector": sector,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_disclosed": salary_disclosed,
                "source": "jadarat",
                "posted_date": posted_date,
                "vision2030_sector": v2030,
                "nitaqat_relevant": sector in ['finance', 'engineering', 'healthcare', 'marketing', 'legal'],
            }

            insert_job_posting(posting)
            saved += 1

            if saved % 100 == 0:
                print(f"  Saved {saved} jobs...")

        except Exception as e:
            skipped += 1
            continue

    print(f"  Jadarat: saved {saved}, skipped {skipped}")
    return saved

def load_linkedin(path: str) -> int:
    print(f"\nLoading LinkedIn dataset from {path}...")
    try:
        df = pd.read_csv(path, encoding='utf-8')
    except:
        df = pd.read_csv(path, encoding='latin-1')

    print(f"  Found {len(df)} rows")
    saved = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            title = str(row.get('Title', '')).strip()
            if not title or title == 'nan':
                skipped += 1
                continue

            company = str(row.get('Company', 'Unknown')).strip()
            location = str(row.get('Location', 'Saudi Arabia')).strip()
            sector = detect_sector(title)
            v2030 = detect_v2030(title + ' ' + company)

            job_date = str(row.get('Date', '')).strip()
            try:
                posted_date = pd.to_datetime(job_date).date().isoformat()
            except:
                posted_date = datetime.now().date().isoformat()

            posting = {
                "title": title,
                "title_ar": None,
                "company": company if company != 'nan' else 'Unknown',
                "location": location if location != 'nan' else 'Saudi Arabia',
                "sector": sector,
                "salary_min": None,
                "salary_max": None,
                "salary_disclosed": False,
                "source": "linkedin",
                "posted_date": posted_date,
                "vision2030_sector": v2030,
                "nitaqat_relevant": sector in ['finance', 'engineering', 'healthcare', 'marketing', 'legal'],
            }

            insert_job_posting(posting)
            saved += 1

            if saved % 100 == 0:
                print(f"  Saved {saved} jobs...")

        except Exception as e:
            skipped += 1
            continue

    print(f"  LinkedIn: saved {saved}, skipped {skipped}")
    return saved

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    total = 0

    jadarat_path = 'data/raw/jadarat.csv'
    if os.path.exists(jadarat_path):
        total += load_jadarat(jadarat_path)
    else:
        print(f"Jadarat file not found at {jadarat_path}")

    linkedin_path = 'data/raw/linkedin_saudi.csv'
    if os.path.exists(linkedin_path):
        total += load_linkedin(linkedin_path)
    else:
        print(f"LinkedIn file not found at {linkedin_path}")

    print(f"\nTotal jobs loaded: {total}")
    print("Done!")