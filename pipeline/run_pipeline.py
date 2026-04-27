import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_scrapers():
    print("\n" + "="*50)
    print("STEP 1: Running job scrapers")
    print("="*50)
    try:
        from pipeline.scrapers.bayt_scraper import scrape_bayt
        asyncio.run(scrape_bayt(max_pages=3))
        print("✓ Bayt scraper complete")
    except Exception as e:
        print(f"✗ Bayt scraper failed: {e}")

def run_rss_monitor():
    print("\n" + "="*50)
    print("STEP 2: Running RSS monitor")
    print("="*50)
    try:
        from pipeline.monitors.rss_monitor import run_rss_monitor as rss
        rss()
        print("✓ RSS monitor complete")
    except Exception as e:
        print(f"✗ RSS monitor failed: {e}")

def run_hrsd_monitor():
    print("\n" + "="*50)
    print("STEP 3: Running HRSD monitor")
    print("="*50)
    try:
        from pipeline.monitors.hrsd_monitor import run_hrsd_monitor as hrsd
        hrsd()
        print("✓ HRSD monitor complete")
    except Exception as e:
        print(f"✗ HRSD monitor failed: {e}")

def run_skills_extractor():
    print("\n" + "="*50)
    print("STEP 4: Running skills extractor")
    print("="*50)
    try:
        from pipeline.processors.skills_extractor import run_skills_extractor as skills
        skills()
        print("✓ Skills extractor complete")
    except Exception as e:
        print(f"✗ Skills extractor failed: {e}")

def run_salary_estimator():
    print("\n" + "="*50)
    print("STEP 5: Running salary estimator")
    print("="*50)
    try:
        from pipeline.processors.salary_estimator import run_salary_estimator as salary
        salary()
        print("✓ Salary estimator complete")
    except Exception as e:
        print(f"✗ Salary estimator failed: {e}")

if __name__ == "__main__":
    start = datetime.now()
    print(f"\n{'='*50}")
    print(f"SAUDI JOB INTELLIGENCE PIPELINE")
    print(f"Started: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    run_scrapers()
    run_rss_monitor()
    run_hrsd_monitor()
    run_skills_extractor()
    run_salary_estimator()

    end = datetime.now()
    duration = (end - start).seconds
    print(f"\n{'='*50}")
    print(f"PIPELINE COMPLETE")
    print(f"Duration: {duration} seconds")
    print(f"Finished: {end.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")