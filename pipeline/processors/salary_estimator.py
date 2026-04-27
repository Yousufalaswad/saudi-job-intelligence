import os
import sys
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_client, insert_salary_benchmark

SALARY_PRIORS = {
    ("Software Engineer", "Technology"): (8000, 15000, 25000),
    ("Data Analyst", "Technology"): (7000, 12000, 20000),
    ("Data Scientist", "Technology"): (10000, 18000, 30000),
    ("Project Manager", "Engineering"): (10000, 18000, 28000),
    ("Civil Engineer", "Engineering"): (7000, 12000, 20000),
    ("Accountant", "Finance"): (5000, 8000, 14000),
    ("Financial Analyst", "Finance"): (8000, 14000, 22000),
    ("Doctor", "Healthcare"): (15000, 25000, 40000),
    ("Nurse", "Healthcare"): (4000, 7000, 12000),
    ("Pharmacist", "Healthcare"): (8000, 14000, 20000),
    ("Marketing Manager", "Marketing"): (10000, 16000, 25000),
    ("Sales Representative", "Marketing"): (4000, 7000, 12000),
    ("HR Manager", "HR"): (10000, 16000, 24000),
    ("Teacher", "Education"): (4000, 7000, 12000),
    ("Lawyer", "Legal"): (10000, 18000, 30000),
}

def estimate_salary_with_llm(title: str, sector: str, groq_client: Groq) -> dict:
    prompt = f"""Estimate the salary range for this job in Saudi Arabia's private sector.

Job Title: {title}
Sector: {sector}

Based on Saudi Arabia 2024-2025 market rates, provide salary estimates in SAR per month.
Return JSON only:
{{"p10": minimum_salary, "p50": median_salary, "p90": maximum_salary, "confidence": 0.0-1.0}}

Example: {{"p10": 8000, "p50": 14000, "p90": 22000, "confidence": 0.75}}
Return only valid JSON."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )
        content = response.choices[0].message.content.strip()
        if '```' in content:
            content = content.split('```')[1].replace('json', '').strip()
        return json.loads(content)
    except:
        return None

def run_salary_estimator():
    print("Running salary estimator...")
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    client = get_client()

    # Save prior benchmarks first
    saved = 0
    for (title, sector), (p10, p50, p90) in SALARY_PRIORS.items():
        try:
            existing = client.table("salary_benchmarks").select("id").eq(
                "job_title", title
            ).eq("sector", sector).execute()
            if not existing.data:
                insert_salary_benchmark({
                    "job_title": title,
                    "sector": sector,
                    "region": "Saudi Arabia",
                    "experience_level": "mid",
                    "salary_p10": p10,
                    "salary_p50": p50,
                    "salary_p90": p90,
                    "sample_size": 0,
                })
                saved += 1
        except:
            continue

    print(f"  Saved {saved} salary benchmarks from priors")

    # Get unique job titles from postings without salary data
    response = client.table("job_postings").select("title, sector").eq(
        "salary_disclosed", False
    ).limit(20).execute()
    jobs = response.data

    llm_saved = 0
    processed_titles = set()

    for job in jobs:
        title = job.get('title', '')
        sector = job.get('sector', 'General')

        if not title or title in processed_titles:
            continue
        processed_titles.add(title)

        # Check if we already have an exact benchmark
        existing = client.table("salary_benchmarks").select("id").eq(
            "job_title", title
        ).execute()
        if existing.data:
            continue

        estimate = estimate_salary_with_llm(title, sector, groq_client)
        if estimate and estimate.get('confidence', 0) > 0.5:
            try:
                insert_salary_benchmark({
                    "job_title": title,
                    "sector": sector,
                    "region": "Saudi Arabia",
                    "experience_level": "mid",
                    "salary_p10": estimate.get('p10', 0),
                    "salary_p50": estimate.get('p50', 0),
                    "salary_p90": estimate.get('p90', 0),
                    "sample_size": 0,
                })
                llm_saved += 1
                print(f"  Estimated: {title} — SAR {estimate.get('p50'):,}/month")
            except:
                continue

    print(f"  LLM estimated {llm_saved} additional salary benchmarks")
    print(f"  Total salary benchmarks in system: {saved + llm_saved}")

if __name__ == "__main__":
    run_salary_estimator()