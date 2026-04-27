import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import (
    load_v2030, load_jobs, apply_global_css,
    section_header, page_header, format_number,
    progress_bar, apply_plotly_theme, kpi_card
)

def show():
    apply_global_css()
    page_header(
        "Vision 2030 Tracker",
        "Real-time hiring progress across Saudi giga-projects · رؤية 2030",
        "متتبع قطاعات رؤية 2030"
    )

    v2030_df = load_v2030()
    jobs_df = load_jobs(limit=1000)

    if v2030_df.empty:
        st.warning("No Vision 2030 data available.")
        return

    total_target = v2030_df['job_target'].sum()
    total_current = v2030_df['jobs_current'].fillna(0).sum()
    overall_pct = (total_current / total_target * 100) if total_target > 0 else 0
    active_sectors = len(v2030_df[v2030_df['jobs_current'].fillna(0) > 0])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card(format_number(total_target), "Total Jobs Target", "إجمالي الوظائف المستهدفة")
    with col2:
        kpi_card(format_number(int(total_current)), "Jobs Tracked", "وظائف مرصودة")
    with col3:
        kpi_card(f"{overall_pct:.1f}%", "Overall Progress", "نسبة الإنجاز")
    with col4:
        kpi_card(str(active_sectors), "Active Sectors", "قطاعات نشطة")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Overall Progress")
    progress_bar(overall_pct)
    st.caption(f"{format_number(int(total_current))} of {format_number(total_target)} target jobs tracked")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Progress by Sector")

    for _, row in v2030_df.sort_values('job_target', ascending=False).iterrows():
        sector = row.get('sector', 'Unknown')
        sector_ar = row.get('sector_ar', '')
        target = int(row.get('job_target', 0) or 0)
        current = int(row.get('jobs_current', 0) or 0)
        pct = (current / target * 100) if target > 0 else 0
        projects = row.get('key_projects', []) or []
        skills = row.get('priority_skills', []) or []

        label = f"**{sector}** · {format_number(current)} / {format_number(target)} jobs · {pct:.1f}%"
        with st.expander(label):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                progress_bar(pct)
                if sector_ar:
                    st.markdown(f'<div class="arabic" style="color:#C6A03C;font-size:0.9rem;margin:0.5rem 0">{sector_ar}</div>', unsafe_allow_html=True)
                if projects:
                    st.markdown(f"**Key Projects:** {' · '.join(projects)}")
                if skills:
                    st.markdown(f"**Priority Skills:** {' · '.join(skills)}")
            with col_b:
                st.metric("Target", format_number(target))
                st.metric("Tracked", format_number(current))
                if pct > 0:
                    st.metric("Progress", f"{pct:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Sector Comparison")

    chart_df = v2030_df[['sector', 'job_target', 'jobs_current']].copy()
    chart_df['jobs_current'] = chart_df['jobs_current'].fillna(0).astype(int)
    chart_df['remaining'] = chart_df['job_target'] - chart_df['jobs_current']
    chart_df = chart_df.sort_values('job_target', ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Jobs Tracked',
        y=chart_df['sector'],
        x=chart_df['jobs_current'],
        orientation='h',
        marker_color='#C6A03C',
    ))
    fig.add_trace(go.Bar(
        name='Remaining',
        y=chart_df['sector'],
        x=chart_df['remaining'],
        orientation='h',
        marker_color='#1E3A5F',
    ))
    fig = apply_plotly_theme(fig, height=450)
    fig.update_layout(
        barmode='stack',
        xaxis_title='Number of Jobs',
        yaxis_title=None,
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Giga Projects Map")

    giga_df = pd.DataFrame([
        {"Project": "NEOM", "Location": "Tabuk", "Investment": "$500B+", "Jobs Target": "380,000", "Status": "🟢 Active"},
        {"Project": "Red Sea Global", "Location": "Red Sea Coast", "Investment": "$15B+", "Jobs Target": "35,000", "Status": "🟢 Active"},
        {"Project": "Qiddiya", "Location": "Riyadh", "Investment": "$8B+", "Jobs Target": "57,000", "Status": "🟢 Active"},
        {"Project": "Diriyah", "Location": "Riyadh", "Investment": "$20B+", "Jobs Target": "178,000", "Status": "🟢 Active"},
        {"Project": "New Murabba", "Location": "Riyadh", "Investment": "$48B+", "Jobs Target": "334,000", "Status": "🟡 Development"},
        {"Project": "AMAALA", "Location": "Red Sea", "Investment": "$5B+", "Jobs Target": "50,000", "Status": "🟡 Development"},
        {"Project": "Riyadh Air", "Location": "Riyadh", "Investment": "$20B+", "Jobs Target": "100,000+", "Status": "🟢 Active"},
        {"Project": "NEOM Green Hydrogen", "Location": "NEOM", "Investment": "$8.4B", "Jobs Target": "40,000", "Status": "🟢 Active"},
    ])
    st.dataframe(giga_df, use_container_width=True, hide_index=True)
    st.caption("Vision 2030 progress updated automatically from news monitoring. Job counts reflect publicly announced figures.")