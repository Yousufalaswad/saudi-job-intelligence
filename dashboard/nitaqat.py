import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date
from utils import (
    load_nitaqat, apply_global_css, section_header,
    page_header, progress_bar, apply_plotly_theme
)

def days_until(deadline_str):
    try:
        deadline = pd.to_datetime(deadline_str).date()
        return (deadline - date.today()).days
    except:
        return None

def show():
    apply_global_css()
    page_header(
        "Nitaqat Tracker",
        "Saudi Saudization compliance tracker · متتبع نطاقات والسعودة",
        "متتبع نطاقات والسعودة"
    )

    st.markdown("""
    <div style="background:rgba(198,160,60,0.08);border:1px solid rgba(198,160,60,0.2);
    border-radius:8px;padding:0.75rem 1rem;font-size:0.8rem;color:#C6A03C;margin-bottom:1rem;">
    ⚖️ <strong>Nitaqat</strong> requires private sector companies to employ a minimum percentage
    of Saudi nationals. Non-compliant companies cannot hire expats or renew work permits.
    </div>
    """, unsafe_allow_html=True)

    nitaqat_df = load_nitaqat()

    if nitaqat_df.empty:
        st.warning("No Nitaqat data available.")
        return

    # Summary KPIs
    col1, col2, col3, col4 = st.columns(4)
    enforced = sum(1 for d in nitaqat_df['deadline'] if days_until(d) is not None and days_until(d) <= 0)
    upcoming = sum(1 for d in nitaqat_df['deadline'] if days_until(d) is not None and 0 < days_until(d) <= 365)
    avg_quota = nitaqat_df['target_quota'].mean()
    full_saudi = len(nitaqat_df[nitaqat_df['target_quota'] >= 100])

    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{enforced}</div><div class="kpi-label">Already Enforced</div><div class="kpi-label-ar">مفعّلة الآن</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{upcoming}</div><div class="kpi-label">Enforced This Year</div><div class="kpi-label-ar">هذا العام</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{avg_quota:.0f}%</div><div class="kpi-label">Avg Target Quota</div><div class="kpi-label-ar">متوسط النسبة المستهدفة</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{full_saudi}</div><div class="kpi-label">100% Saudi Roles</div><div class="kpi-label-ar">وظائف للسعوديين فقط</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Profession Quotas — Active & Upcoming")

    for _, row in nitaqat_df.sort_values('target_quota', ascending=False).iterrows():
        quota = row.get('target_quota', 0) or 0
        profession = row.get('profession', 'Unknown')
        profession_ar = row.get('profession_ar', '')
        deadline = row.get('deadline', 'TBD')
        min_salary = row.get('min_salary', 0)
        sector = row.get('sector', '')
        days = days_until(deadline)

        if quota >= 100:
            color = "#EF4444"
            badge = '<span class="badge-red">🔴 100% Saudi</span>'
        elif quota >= 60:
            color = "#F59E0B"
            badge = f'<span class="badge-red">🔴 {quota:.0f}% Required</span>'
        elif quota >= 40:
            color = "#F59E0B"
            badge = f'<span class="badge-amber">🟠 {quota:.0f}% Required</span>'
        else:
            color = "#10B981"
            badge = f'<span class="badge-green">🟡 {quota:.0f}% Required</span>'

        if days is not None and days <= 0:
            status = "🔴 ENFORCED"
        elif days is not None and days <= 90:
            status = f"🟠 {days} days left"
        elif days is not None:
            status = f"🟡 {days} days left"
        else:
            status = "⚪ TBD"

        with st.expander(f"{profession}  ·  {badge}  ·  {status}", expanded=False):
            ca, cb, cc = st.columns(3)
            with ca:
                st.markdown(f'<div class="arabic" style="font-size:1.1rem;color:#C6A03C">{profession_ar}</div>', unsafe_allow_html=True)
                st.caption(f"Sector: {sector}")
            with cb:
                st.metric("Current Quota", f"{row.get('current_quota',0):.0f}%")
                st.metric("Target Quota", f"{quota:.0f}%")
            with cc:
                st.metric("Deadline", str(deadline)[:10] if deadline else "TBD")
                if min_salary and min_salary > 0:
                    st.metric("Min Salary", f"SAR {int(min_salary):,}")
            progress_bar(quota, color)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Quota Comparison Chart")

    chart_df = nitaqat_df[['profession', 'current_quota', 'target_quota']].copy().sort_values('target_quota')
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Current Quota',
        y=chart_df['profession'],
        x=chart_df['current_quota'],
        orientation='h',
        marker_color='#1E3A5F',
    ))
    fig.add_trace(go.Bar(
        name='Target Quota',
        y=chart_df['profession'],
        x=chart_df['target_quota'],
        orientation='h',
        marker_color='#C6A03C',
        opacity=0.7,
    ))
    fig = apply_plotly_theme(fig, height=500)
    fig.update_layout(
        barmode='overlay',
        xaxis_title='Required Saudi Nationals (%)',
        yaxis_title=None,
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    fig.add_vline(x=50, line_dash="dash", line_color="#EF4444",
                  annotation_text="50%", annotation_font_color="#EF4444")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Nitaqat 2026–2028 Program")
    upcoming_df = pd.DataFrame([
        {"Profession": "Marketing & Sales", "New Quota": "60%", "Deadline": "Apr 2026", "Min Salary": "SAR 5,500", "Status": "🔴 Now Active"},
        {"Profession": "Accounting", "New Quota": "70%", "Deadline": "Oct 2028", "Min Salary": "TBD", "Status": "🟡 Upcoming"},
        {"Profession": "Engineering (SCE)", "New Quota": "30%", "Deadline": "Jul 2025", "Min Salary": "SAR 8,000", "Status": "🔴 Enforced"},
        {"Profession": "Consulting Phase 2", "New Quota": "TBD", "Deadline": "2026", "Min Salary": "TBD", "Status": "🟠 Watch"},
        {"Profession": "269 More Professions", "New Quota": "Various", "Deadline": "2026–2028", "Min Salary": "Various", "Status": "🟠 Announced"},
    ])
    st.dataframe(upcoming_df, use_container_width=True, hide_index=True)
    st.caption("Data sourced from HRSD, HRDF, and automated news monitoring. Updated when new regulations are published.")