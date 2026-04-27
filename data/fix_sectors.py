import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_client
from dotenv import load_dotenv
load_dotenv()

SECTOR_KEYWORDS = {
    'technology': [
        'software', 'developer', 'engineer', 'data', 'ai ', 'cloud', 'cyber',
        'python', 'java', 'react', 'angular', 'node', 'devops', 'backend',
        'frontend', 'fullstack', 'mobile', 'ios', 'android', 'unity',
        'game dev', 'ux', 'ui ', 'product', 'scrum', 'agile', 'qa ',
        'quality assurance', 'testing', 'soc ', 'soar', 'siem', 'network',
        'infrastructure', 'architect', 'solutions', 'system', 'database',
        'middleware', 'integration', 'api ', 'erp', 'sap', 'oracle',
        'microsoft', 'aws', 'azure', 'gcp', 'linux', 'unix', 'it ',
        'information technology', 'digital', 'tech', 'cto', 'cio',
        'business analyst', 'business system', 'business intelligence',
        'power bi', 'tableau', 'machine learning', 'deep learning',
        'nlp', 'computer vision', 'robotics', 'automation', 'rpa',
        'blockchain', 'metaverse', 'vr ', 'ar ', 'iot', 'embedded',
        'firmware', 'hardware', 'semiconductor', 'release', 'delivery',
        'program manager', 'project manager', 'pmo', 'portfolio',
        'تقنية', 'برمجة', 'مطور', 'شبكات', 'أمن معلومات', 'بيانات',
        'ذكاء اصطناعي', 'حوسبة', 'تحليل', 'نظم معلومات',
    ],
    'healthcare': [
        'doctor', 'nurse', 'pharmacy', 'medical', 'health', 'hospital',
        'clinic', 'surgeon', 'dentist', 'chemist', 'chemistry', 'biology',
        'lab ', 'laboratory', 'radiology', 'physiotherapy', 'nutrition',
        'optometrist', 'veterinary', 'paramedic', 'emt', 'hse',
        'safety', 'environmental health', 'occupational health',
        'clinical', 'pathology', 'oncology', 'cardiology', 'pediatric',
        'psychiatric', 'midwife', 'sonographer', 'audiologist',
        'طبيب', 'ممرض', 'صيدلة', 'صحة', 'مستشفى', 'أشعة', 'تغذية',
        'مختبر', 'عيادة', 'جراح',
    ],
    'engineering': [
        'civil', 'mechanical', 'electrical', 'structural', 'construction',
        'autocad', 'revit', 'bim', 'hvac', 'plumbing', 'piping',
        'instrumentation', 'process', 'chemical engineer', 'petroleum',
        'oil ', 'gas ', 'drilling', 'reservoir', 'geologist', 'surveyor',
        'quantity surveyor', 'site engineer', 'field engineer',
        'maintenance', 'reliability', 'rotating equipment', 'static',
        'welding', 'fabrication', 'commissioning', 'procurement',
        'supply chain', 'logistics', 'warehouse', 'operations',
        'plant', 'facility', 'asset', 'epc', 'pmc',
        'مهندس', 'هندسة', 'مشاريع', 'صيانة', 'إنشاء', 'تشغيل',
        'بترول', 'كيمياء', 'ميكانيكا', 'كهرباء',
    ],
    'finance': [
        'account', 'finance', 'audit', 'banker', 'banking', 'investment',
        'tax', 'treasury', 'controller', 'cfo', 'financial', 'budget',
        'forecast', 'risk', 'compliance', 'aml', 'kyc', 'insurance',
        'actuary', 'cpa', 'cfa', 'acca', 'ifrs', 'vat', 'zakat',
        'محاسب', 'مالية', 'تدقيق', 'بنك', 'استثمار', 'ميزانية',
    ],
    'marketing': [
        'marketing', 'sales', 'brand', 'advertising', 'digital marketing',
        'seo', 'sem', 'social media', 'content', 'copywriter', 'creative',
        'campaign', 'crm', 'customer', 'retail', 'ecommerce', 'growth',
        'performance marketing', 'media buyer', 'influencer',
        'تسويق', 'مبيعات', 'إعلان', 'علامة تجارية', 'عملاء',
    ],
    'tourism': [
        'hotel', 'hospitality', 'tourism', 'chef', 'cook', 'restaurant',
        'catering', 'front office', 'housekeeping', 'concierge', 'butler',
        'food beverage', 'f&b', 'barista', 'sommelier', 'event',
        'travel', 'airline', 'cabin crew', 'guest',
        'فندق', 'سياحة', 'ضيافة', 'طباخ', 'مطعم',
    ],
    'education': [
        'teacher', 'professor', 'instructor', 'trainer', 'tutor',
        'academic', 'curriculum', 'e-learning', 'learning development',
        'l&d', 'training', 'education', 'school', 'university',
        'معلم', 'أستاذ', 'تدريب', 'مدرس', 'تعليم',
    ],
    'legal': [
        'lawyer', 'legal', 'attorney', 'compliance', 'regulatory',
        'contract', 'litigation', 'arbitration', 'paralegal',
        'محامي', 'قانون', 'امتثال', 'تنظيمي',
    ],
    'hr': [
        'human resources', 'hr ', 'recruitment', 'talent acquisition',
        'talent management', 'compensation', 'benefits', 'payroll',
        'organizational', 'people', 'workforce',
        'موارد بشرية', 'توظيف', 'رواتب',
    ],
}

def classify_sector(title: str) -> str:
    if not title:
        return 'other'
    text = title.lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(kw.lower() in text for kw in keywords):
            return sector
    return 'other'

def fix_sectors():
    client = get_client()
    print("Fetching all jobs...")

    # Fetch in batches
    batch_size = 1000
    offset = 0
    all_jobs = []

    while True:
        response = client.table("job_postings").select("id, title").range(
            offset, offset + batch_size - 1
        ).execute()
        batch = response.data
        if not batch:
            break
        all_jobs.extend(batch)
        offset += batch_size
        if len(batch) < batch_size:
            break

    print(f"Found {len(all_jobs)} jobs to reclassify")

    updates = {}
    for job in all_jobs:
        new_sector = classify_sector(job.get('title', ''))
        updates.setdefault(new_sector, []).append(job['id'])

    print("\nNew sector distribution:")
    for sector, ids in sorted(updates.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {sector}: {len(ids)}")

    print("\nUpdating database...")
    total_updated = 0
    for sector, ids in updates.items():
        for i in range(0, len(ids), 100):
            batch_ids = ids[i:i+100]
            client.table("job_postings").update(
                {"sector": sector}
            ).in_("id", batch_ids).execute()
            total_updated += len(batch_ids)

    print(f"Updated {total_updated} jobs")
    print("Done!")

if __name__ == "__main__":
    fix_sectors()