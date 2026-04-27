import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import (
    load_skills, apply_global_css, section_header,
    page_header, apply_plotly_theme, SECTOR_COLORS
)

def show():
    apply_global_css()
    page_header(
        "Skills Intelligence",
        "Most in-demand skills in the Saudi job market · المهارات الأكثر طلباً",
        "تحليل المهارات المطلوبة"
    )

    skills_df = load_skills()

    if skills_df.empty:
        st.warning("No skills data available yet. Run the pipeline first.")
        return

    # Filters
    col1, col2 = st.columns([2, 1])
    with col1:
        sectors = ['All'] + sorted(skills_df['sector'].unique().tolist()) if 'sector' in skills_df.columns else ['All']
        selected_sector = st.selectbox("Filter by sector", sectors)
    with col2:
        top_n = st.slider("Top N skills", 10, 38, 20)

    filtered = skills_df.copy()
    if selected_sector != 'All':
        filtered = filtered[filtered['sector'] == selected_sector]

    section_header("Top In-Demand Skills")

    if 'posting_count' in filtered.columns:
        top_skills = filtered.nlargest(top_n, 'posting_count')

        fig = go.Figure(go.Bar(
            x=top_skills['posting_count'],
            y=top_skills['skill_name'],
            orientation='h',
            marker=dict(
                color=top_skills['sector'].map(lambda x: SECTOR_COLORS.get(x.lower() if x else 'other', '#374151')),
                opacity=0.85,
                line=dict(width=0),
            ),
            text=top_skills['posting_count'],
            textposition='outside',
            textfont=dict(color='#6B7FA3', size=11),
        ))
        fig = apply_plotly_theme(fig, height=500)
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Job Postings",
            yaxis_title=None,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Skills by Sector")

    if 'sector' in skills_df.columns:
        sector_counts = skills_df.groupby('sector')['posting_count'].sum().reset_index()
        sector_counts.columns = ['sector', 'total']
        sector_counts = sector_counts.sort_values('total', ascending=False)

        fig2 = go.Figure(go.Bar(
            x=sector_counts['sector'].str.title(),
            y=sector_counts['total'],
            marker=dict(
                color=sector_counts['sector'].map(lambda x: SECTOR_COLORS.get(x.lower(), '#374151')),
                opacity=0.85,
                line=dict(width=0),
            ),
            text=sector_counts['total'],
            textposition='outside',
            textfont=dict(color='#6B7FA3', size=11),
        ))
        fig2 = apply_plotly_theme(fig2, height=300)
        fig2.update_layout(xaxis_title=None, yaxis_title="Demand Score", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Skills Gap Analysis")

    gap_data = [
        {"Skill": "AI / Machine Learning", "Demand": "🔴 Very High", "Supply": "Low", "Gap": "Critical"},
        {"Skill": "Cybersecurity", "Demand": "🔴 Very High", "Supply": "Low", "Gap": "Critical"},
        {"Skill": "Cloud Computing (AWS/Azure)", "Demand": "🟠 High", "Supply": "Medium", "Gap": "High"},
        {"Skill": "Data Engineering", "Demand": "🔴 Very High", "Supply": "Low", "Gap": "Critical"},
        {"Skill": "Arabic NLP", "Demand": "🟠 Growing", "Supply": "Very Low", "Gap": "Critical"},
        {"Skill": "Renewable Energy Engineering", "Demand": "🟠 Growing", "Supply": "Low", "Gap": "Critical"},
        {"Skill": "Healthcare (Nursing)", "Demand": "🔴 Very High", "Supply": "Medium", "Gap": "High"},
        {"Skill": "Financial Analysis (CFA/CPA)", "Demand": "🟠 High", "Supply": "Medium", "Gap": "Medium"},
        {"Skill": "Hospitality Management", "Demand": "🟠 High", "Supply": "Low", "Gap": "High"},
        {"Skill": "Project Management (PMP)", "Demand": "🟠 High", "Supply": "Medium", "Gap": "Medium"},
    ]
    st.dataframe(pd.DataFrame(gap_data), use_container_width=True, hide_index=True, height=350)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("All Skills Data")
    cols = [c for c in ['skill_name', 'sector', 'posting_count', 'week_date'] if c in skills_df.columns]
    st.dataframe(
        skills_df[cols].sort_values('posting_count', ascending=False).rename(columns={
            'skill_name': 'Skill', 'sector': 'Sector',
            'posting_count': 'Postings', 'week_date': 'Week',
        }),
        use_container_width=True, hide_index=True, height=300,
    )