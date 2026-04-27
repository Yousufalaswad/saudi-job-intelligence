import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Saudi Job Market Intelligence",
    page_icon="🇸🇦",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.utils import apply_global_css
apply_global_css()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 0.5rem;">
        <div style="font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#C6A03C;font-weight:700;">
            Saudi Arabia
        </div>
        <div style="font-size:1.3rem;font-weight:800;color:#FFFFFF;line-height:1.2;margin:0.25rem 0;">
            Job Market<br>Intelligence
        </div>
        <div style="font-family:'Noto Sans Arabic',sans-serif;direction:rtl;color:#6B7FA3;font-size:0.8rem;margin-top:0.25rem;">
            مؤشر سوق العمل السعودي
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="border-color:rgba(198,160,60,0.2);margin:0.75rem 0"/>', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.72rem;color:#6B7FA3;padding:0 0 0.5rem;">
        <span class="live-dot"></span>
        <span style="color:#10B981;font-weight:600;">LIVE</span>
        &nbsp;·&nbsp; Updated daily
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "",
        [
            "📊  Market Overview",
            "🔧  Skills Intelligence",
            "💰  Salary Benchmarks",
            "⚖️  Nitaqat Tracker",
            "🏗️  Vision 2030",
        ],
        label_visibility="collapsed"
    )

    st.markdown('<hr style="border-color:rgba(198,160,60,0.2);margin:0.75rem 0"/>', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.7rem;color:#4A5A7A;line-height:2;">
        📡 Monitoring 400+ sources<br>
        🤖 LLM-powered extraction<br>
        ⚖️ Nitaqat compliance tracker<br>
        🏗️ Vision 2030 sector tracking
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="border-color:rgba(198,160,60,0.2);margin:0.75rem 0"/>', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.68rem;color:#4A5A7A;">
        Built by <span style="color:#C6A03C;font-weight:600;">Yousuf Alaswad</span><br>
        FIU Computer Engineering · 2026
    </div>
    """, unsafe_allow_html=True)

# Route to pages
if "Overview" in page:
    from dashboard.overview import show
    show()
elif "Skills" in page:
    from dashboard.skills import show
    show()
elif "Salary" in page:
    from dashboard.salary import show
    show()
elif "Nitaqat" in page:
    from dashboard.nitaqat import show
    show()
elif "Vision" in page:
    from dashboard.vision2030 import show
    show()