import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import (
    load_jobs, apply_global_css,
    kpi_card, section_header, page_header,
    format_number, apply_plotly_theme,
    SECTOR_COLORS, SECTOR_ICONS
)

def show():
    apply_global_css()
    page_header(
        "Saudi Job Market",
        "Real-time labor market intelligence · سوق العمل السعودي",
        "نظرة عامة على سوق العمل"
    )

    jobs_df = load_jobs(limit=1000)

    if jobs_df.empty:
        st.warning("No job data available yet. Run the pipeline first.")
        return

    # KPI row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        kpi_card(format_number(len(jobs_df)), "Jobs Tracked", "وظائف مرصودة")
    with col2:
        companies = jobs_df['company'].nunique() if 'company' in jobs_df.columns else 0
        kpi_card(format_number(companies), "Companies Hiring", "شركات توظف")
    with col3:
        sectors = jobs_df[jobs_df['sector'] != 'other']['sector'].nunique() if 'sector' in jobs_df.columns else 0
        kpi_card(str(sectors), "Active Sectors", "قطاعات نشطة")
    with col4:
        with_salary = int(jobs_df['salary_disclosed'].sum()) if 'salary_disclosed' in jobs_df.columns else 0
        pct = int(with_salary / len(jobs_df) * 100) if len(jobs_df) > 0 else 0
        kpi_card(f"{pct}%", "Salary Disclosed", "وظائف بمرتب معلن")
    with col5:
        v2030_jobs = jobs_df['vision2030_sector'].notna().sum() if 'vision2030_sector' in jobs_df.columns else 0
        kpi_card(format_number(v2030_jobs), "V2030 Aligned", "رؤية 2030")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row
    col_left, col_right = st.columns([3, 2])

    with col_left:
        section_header("Jobs by Sector")
        if 'sector' in jobs_df.columns:
            sector_df = jobs_df[jobs_df['sector'] != 'other']['sector'].value_counts().reset_index()
            sector_df.columns = ['sector', 'count']
            sector_df['color'] = sector_df['sector'].map(lambda x: SECTOR_COLORS.get(x, '#374151'))
            sector_df['label'] = sector_df['sector'].map(
                lambda x: f"{SECTOR_ICONS.get(x, '📋')} {x.title()}"
            )
            fig = go.Figure(go.Bar(
                x=sector_df['count'],
                y=sector_df['label'],
                orientation='h',
                marker=dict(
                    color=sector_df['color'],
                    opacity=0.85,
                    line=dict(width=0)
                ),
                text=sector_df['count'],
                textposition='outside',
                textfont=dict(color='#6B7FA3', size=11),
            ))
            fig = apply_plotly_theme(fig, height=380)
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title=None,
                yaxis_title=None,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        section_header("Location Distribution")
        if 'location' in jobs_df.columns:
            loc_df = jobs_df['location'].value_counts().head(7).reset_index()
            loc_df.columns = ['location', 'count']
            fig2 = go.Figure(go.Pie(
                labels=loc_df['location'],
                values=loc_df['count'],
                hole=0.55,
                marker=dict(
                    colors=['#C6A03C', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'],
                    line=dict(color='#020917', width=2)
                ),
                textfont=dict(color='#E8EDF5', size=11),
                showlegend=True,
            ))
            fig2 = apply_plotly_theme(fig2, height=380)
            fig2.update_layout(
                legend=dict(
                    orientation='v',
                    font=dict(size=10, color='#6B7FA3'),
                    bgcolor='rgba(0,0,0,0)',
                ),
                annotations=[dict(
                    text=f"<b>{format_number(len(jobs_df))}</b><br>jobs",
                    x=0.5, y=0.5,
                    font=dict(size=14, color='#C6A03C'),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Top companies
    section_header("Top Hiring Companies")
    if 'company' in jobs_df.columns:
        top_co = jobs_df[
            (jobs_df['company'] != 'Unknown') & (jobs_df['company'].notna())
        ]['company'].value_counts().head(12).reset_index()
        top_co.columns = ['company', 'count']

        fig3 = go.Figure(go.Bar(
            x=top_co['company'],
            y=top_co['count'],
            marker=dict(
                color=top_co['count'],
                colorscale=[[0, '#0D1F3C'], [0.5, '#C6A03C'], [1, '#F0C755']],
                showscale=False,
                line=dict(width=0),
            ),
            text=top_co['count'],
            textposition='outside',
            textfont=dict(color='#6B7FA3', size=11),
        ))
        fig3 = apply_plotly_theme(fig3, height=300)
        fig3.update_layout(
            xaxis_tickangle=-35,
            yaxis_title=None,
            xaxis_title=None,
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Jobs table
    section_header("Live Job Postings")
    col_s, col_f = st.columns([3, 1])
    with col_s:
        search = st.text_input("", placeholder="🔍  Search by title, company...")
    with col_f:
        sector_opts = ['All Sectors'] + sorted([
            s for s in jobs_df['sector'].unique() if s != 'other'
        ]) if 'sector' in jobs_df.columns else ['All Sectors']
        sel_sector = st.selectbox("", sector_opts, label_visibility="collapsed")

    display = jobs_df.copy()
    if search:
        mask = (
            display['title'].str.contains(search, case=False, na=False) |
            display['company'].str.contains(search, case=False, na=False)
        )
        display = display[mask]
    if sel_sector != 'All Sectors':
        display = display[display['sector'] == sel_sector]

    cols = [c for c in ['title', 'company', 'location', 'sector', 'source', 'posted_date'] if c in display.columns]
    st.dataframe(
        display[cols].head(50).rename(columns={
            'title': 'Job Title', 'company': 'Company',
            'location': 'Location', 'sector': 'Sector',
            'source': 'Source', 'posted_date': 'Posted',
        }),
        use_container_width=True,
        hide_index=True,
        height=400,
    )