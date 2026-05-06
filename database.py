import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Debug — remove after fixing
import logging
logging.warning(f"SUPABASE_URL loaded: {bool(SUPABASE_URL)} — starts with: {str(SUPABASE_URL)[:30] if SUPABASE_URL else 'NONE'}")    

def get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_nitaqat_rules():
    client = get_client()
    response = client.table("nitaqat_rules").select("*").execute()
    return response.data

def get_v2030_targets():
    client = get_client()
    response = client.table("v2030_targets").select("*").execute()
    return response.data

def get_job_postings(limit=100, sector=None):
    client = get_client()
    query = client.table("job_postings").select("*").order("scraped_at", desc=True).limit(limit)
    if sector:
        query = query.eq("sector", sector)
    response = query.execute()
    return response.data

def get_skills_demand(sector=None):
    client = get_client()
    query = client.table("skills_demand").select("*").order("posting_count", desc=True)
    if sector:
        query = query.eq("sector", sector)
    response = query.execute()
    return response.data

def get_salary_benchmarks(job_title=None, sector=None):
    client = get_client()
    query = client.table("salary_benchmarks").select("*")
    if job_title:
        query = query.ilike("job_title", f"%{job_title}%")
    if sector:
        query = query.eq("sector", sector)
    response = query.execute()
    return response.data

def insert_job_posting(posting: dict):
    client = get_client()
    response = client.table("job_postings").insert(posting).execute()
    return response.data

def insert_skill_demand(skill: dict):
    client = get_client()
    response = client.table("skills_demand").insert(skill).execute()
    return response.data

def insert_salary_benchmark(benchmark: dict):
    client = get_client()
    response = client.table("salary_benchmarks").insert(benchmark).execute()
    return response.data

def update_v2030_target(sector: str, jobs_current: int):
    client = get_client()
    response = client.table("v2030_targets").update(
        {"jobs_current": jobs_current}
    ).eq("sector", sector).execute()
    return response.data

def upsert_nitaqat_rule(rule: dict):
    client = get_client()
    response = client.table("nitaqat_rules").upsert(rule).execute()
    return response.data