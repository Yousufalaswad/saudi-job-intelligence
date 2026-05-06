import streamlit as st
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import (
    get_job_postings, get_skills_demand,
    get_salary_benchmarks, get_nitaqat_rules, get_v2030_targets
)

def apply_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+Arabic:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif !important;
        background-color: #020917 !important;
        color: #E8EDF5 !important;
    }

    .main, .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main {
        background-color: #020917 !important;
    }

    [data-testid="stHeader"] {
        background-color: #020917 !important;
    }

    [data-testid="stToolbar"] {
        background-color: #020917 !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 1400px !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #040E24 0%, #020917 100%) !important;
        border-right: 1px solid rgba(198, 160, 60, 0.2) !important;
    }
    [data-testid="stSidebar"] * { color: #E8EDF5 !important; }

    .kpi-card {
        background: linear-gradient(135deg, #0A1628 0%, #0D1F3C 100%);
        border: 1px solid rgba(198, 160, 60, 0.25);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s ease;
        margin-bottom: 0.5rem;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #C6A03C, #F0C755);
    }
    .kpi-card:hover { border-color: rgba(198, 160, 60, 0.6); }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F0C755, #C6A03C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    .kpi-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #6B7FA3;
        margin-top: 0.35rem;
        font-weight: 600;
    }
    .kpi-label-ar {
        font-size: 0.68rem;
        color: #4A5A7A;
        font-family: 'Noto Sans Arabic', sans-serif;
        direction: rtl;
        margin-top: 0.15rem;
    }

    .section-header {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #C6A03C;
        font-weight: 700;
        margin: 1.25rem 0 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(198,160,60,0.4), transparent);
    }

    .page-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #C6A03C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.15rem;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 0.72rem;
        color: #6B7FA3;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 1.5rem;
    }

    .progress-track {
        height: 6px;
        background: rgba(198,160,60,0.1);
        border-radius: 3px;
        overflow: hidden;
        margin: 0.4rem 0;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #C6A03C, #F0C755);
        border-radius: 3px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(198, 160, 60, 0.15) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"] {
        background: #0A1628 !important;
        border: 1px solid rgba(198,160,60,0.15) !important;
        border-radius: 8px !important;
    }

    [data-testid="stTextInput"] input {
        background: #0A1628 !important;
        border: 1px solid rgba(198,160,60,0.25) !important;
        color: #E8EDF5 !important;
        border-radius: 6px !important;
    }

    [data-testid="stSelectbox"] > div > div {
        background: #0A1628 !important;
        border: 1px solid rgba(198,160,60,0.25) !important;
        color: #E8EDF5 !important;
        border-radius: 6px !important;
    }

    [data-testid="stAlert"] {
        background: rgba(198,160,60,0.08) !important;
        border: 1px solid rgba(198,160,60,0.2) !important;
        border-radius: 8px !important;
        color: #E8EDF5 !important;
    }

    hr { border-color: rgba(198,160,60,0.15) !important; }

    .arabic {
        direction: rtl;
        text-align: right;
        font-family: 'Noto Sans Arabic', sans-serif;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    .live-dot {
        display: inline-block;
        width: 6px; height: 6px;
        background: #10B981;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 6px;
        vertical-align: middle;
    }

    [data-testid="stRadio"] label {
        color: #6B7FA3 !important;
        font-size: 0.85rem !important;
    }

    .badge-red {
        background: rgba(220,38,38,0.15);
        color: #F87171;
        border: 1px solid rgba(220,38,38,0.3);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-amber {
        background: rgba(217,119,6,0.15);
        color: #FCD34D;
        border: 1px solid rgba(217,119,6,0.3);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-green {
        background: rgba(16,185,129,0.15);
        color: #6EE7B7;
        border: 1px solid rgba(16,185,129,0.3);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_plotly_theme(fig, height=400):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,22,40,0.8)",
        font=dict(color="#E8EDF5", family="Syne"),
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(198,160,60,0.2)",
            font=dict(color="#6B7FA3", size=11)
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(198,160,60,0.08)",
        linecolor="rgba(198,160,60,0.15)",
        tickfont=dict(color="#6B7FA3", size=11),
    )
    fig.update_yaxes(
        gridcolor="rgba(198,160,60,0.08)",
        linecolor="rgba(198,160,60,0.15)",
        tickfont=dict(color="#6B7FA3", size=11),
    )
    return fig


def kpi_card(value: str, label: str, label_ar: str = ""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {f'<div class="kpi-label-ar">{label_ar}</div>' if label_ar else ''}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str, title_ar: str = ""):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if title_ar:
        st.markdown(
            f'<div class="arabic" style="font-size:1rem;color:#C6A03C;margin-bottom:0.2rem">{title_ar}</div>',
            unsafe_allow_html=True
        )
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def progress_bar(pct: float, color: str = "#C6A03C"):
    pct_clamped = min(max(pct, 0), 100)
    st.markdown(f"""
    <div class="progress-track">
        <div class="progress-fill" style="width:{pct_clamped}%;background:linear-gradient(90deg,{color},{color}CC)"></div>
    </div>
    """, unsafe_allow_html=True)


def format_number(n) -> str:
    if n is None:
        return "N/A"
    try:
        n = int(n)
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n/1_000:.0f}K"
        return str(n)
    except:
        return "N/A"


def format_salary(amount) -> str:
    if not amount:
        return "N/A"
    return f"SAR {int(amount):,}"


@st.cache_data(ttl=3600)
def load_jobs(limit=1000):
    data = get_job_postings(limit=limit)
    return pd.DataFrame(data) if data else pd.DataFrame()


@st.cache_data(ttl=3600)
def load_skills():
    data = get_skills_demand()
    return pd.DataFrame(data) if data else pd.DataFrame()


@st.cache_data(ttl=3600)
def load_salaries():
    data = get_salary_benchmarks()
    return pd.DataFrame(data) if data else pd.DataFrame()


@st.cache_data(ttl=3600)
def load_nitaqat():
    data = get_nitaqat_rules()
    return pd.DataFrame(data) if data else pd.DataFrame()


@st.cache_data(ttl=3600)
def load_v2030():
    data = get_v2030_targets()
    return pd.DataFrame(data) if data else pd.DataFrame()


SECTOR_COLORS = {
    'technology': '#3B82F6',
    'healthcare': '#10B981',
    'engineering': '#F59E0B',
    'finance': '#8B5CF6',
    'marketing': '#EF4444',
    'tourism': '#06B6D4',
    'education': '#C6A03C',
    'legal': '#6366F1',
    'hr': '#EC4899',
    'other': '#1E293B',
}

SECTOR_ICONS = {
    'technology': '💻',
    'healthcare': '🏥',
    'engineering': '⚙️',
    'finance': '💰',
    'marketing': '📢',
    'tourism': '✈️',
    'education': '📚',
    'legal': '⚖️',
    'hr': '👥',
    'other': '📋',
}