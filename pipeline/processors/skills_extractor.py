import os
import sys
import json
from datetime import datetime, date
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_client

SAUDI_SKILLS_TAXONOMY = {
    "Technology": [
        "Python", "SQL", "JavaScript", "React", "Angular", "Node.js",
        "AWS", "Azure", "GCP", "Machine Learning", "Deep Learning",
        "Data Analysis", "Cybersecurity", "Cloud Computing", "AI",
        "Power BI", "Tableau", "DevOps", "Docker", "Kubernetes",
        "Java", "C++", "C#", ".NET", "PHP", "Ruby", "Swift", "Kotlin",
        "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Blockchain",
        "برمجة", "بيانات", "ذكاء اصطناعي", "أمن معلومات", "تقنية",
    ],
    "Engineering": [
        "Civil Engineering", "Mechanical Engineering", "Electrical Engineering",
        "Project Management", "AutoCAD", "Revit", "BIM", "HVAC",
        "Structural Engineering", "Chemical Engineering", "Petroleum Engineering",
        "Process Engineering", "Quality Control", "HSE", "Safety",
        "هندسة مدنية", "هندسة ميكانيكية", "هندسة كهربائية", "مشاريع",
    ],
    "Finance": [
        "Accounting", "Auditing", "Financial Analysis", "CPA", "IFRS",
        "VAT", "Zakat", "Treasury", "Risk Management", "Compliance",
        "AML", "KYC", "Investment", "CFA", "ACCA", "Budgeting",
        "محاسبة", "تدقيق", "تحليل مالي", "مخاطر",
    ],
    "Healthcare": [
        "Nursing", "Pharmacy", "Radiology", "Surgery", "Dentistry",
        "Physiotherapy", "Nutrition", "Clinical Research", "Laboratory",
        "Medical Coding", "Healthcare Management", "EMR",
        "تمريض", "صيدلة", "أشعة", "طب أسنان", "تغذية",
    ],
    "Marketing": [
        "Digital Marketing", "SEO", "SEM", "Content Marketing",
        "Social Media", "Brand Management", "CRM", "Salesforce",
        "Email Marketing", "Google Analytics", "Performance Marketing",
        "تسويق رقمي", "وسائل التواصل", "إدارة العلامة التجارية",
    ],
    "Soft Skills": [
        "Leadership", "Communication", "Problem Solving", "Teamwork",
        "Project Management", "Presentation", "Negotiation", "Arabic",
        "English", "Bilingual", "قيادة", "تواصل", "إدارة",
    ],
}

def extract_skills_from_posting(title: str, description: str = "") -> list:
    found_skills = []
    text = (title + " " + description).lower()
    for sector, skills in SAUDI_SKILLS_TAXONOMY.items():
        for skill in skills:
            if skill.lower() in text:
                found_skills.append({"skill": skill, "sector": sector})
    return found_skills

def extract_skills_with_llm(jobs: list, groq_client: Groq) -> dict:
    if not jobs:
        return {}

    titles = [j.get('title', '') for j in jobs[:50] if j.get('title')]
    titles_text = "\n".join(titles)

    prompt = f"""Analyze these Saudi Arabia job titles and extract the most in-demand skills.

Job titles:
{titles_text}

Return a JSON object with skill names as keys and count estimates as values.
Focus on technical skills, certifications, and domain expertise.
Return top 30 skills only. Example: {{"Python": 8, "Project Management": 6}}
Return only valid JSON, nothing else."""

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
        return json.loads(content)
    except:
        return {}

def run_skills_extractor():
    print("Running skills extractor...")
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    client = get_client()

    response = client.table("job_postings").select("*").order(
        "scraped_at", desc=True
    ).limit(1000).execute()
    jobs = response.data

    if not jobs:
        print("  No jobs found to process")
        return

    print(f"  Processing {len(jobs)} jobs...")

    skill_counts = {}
    skill_sectors = {}

    for job in jobs:
        title = job.get('title', '')
        skills = extract_skills_from_posting(title)
        for item in skills:
            skill = item['skill']
            sector = item['sector']
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
            skill_sectors[skill] = sector

    llm_skills = extract_skills_with_llm(jobs, groq_client)
    for skill, count in llm_skills.items():
        if skill not in skill_counts:
            skill_counts[skill] = count
            skill_sectors[skill] = "General"
        else:
            skill_counts[skill] = max(skill_counts[skill], count)

    today = date.today().isoformat()

    # Delete today's records and reinsert fresh
    try:
        client.table("skills_demand").delete().eq("week_date", today).execute()
        print(f"  Cleared today's existing skills data")
    except Exception as e:
        print(f"  Could not clear existing data: {e}")

    saved = 0
    for skill_name, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:50]:
        try:
            client.table("skills_demand").insert({
                "skill_name": skill_name,
                "sector": skill_sectors.get(skill_name, "General"),
                "region": "Saudi Arabia",
                "posting_count": count,
                "week_date": today,
                "trend_7d": 0.0,
                "trend_30d": 0.0,
            }).execute()
            saved += 1
        except Exception as e:
            continue

    print(f"  Saved {saved} skills to database")
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"  Top skills: {', '.join([f'{s}({c})' for s,c in top_skills])}")

if __name__ == "__main__":
    run_skills_extractor()