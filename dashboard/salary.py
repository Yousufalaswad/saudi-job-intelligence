import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import (
    load_salaries, apply_global_css, section_header,
    page_header, format_salary, apply_plotly_theme
)

def show():
    apply_global_css()
    page_header(
        "Salary Intelligence",
        "Saudi Arabia salary benchmarks by role and sector · معايير الرواتب",
        "تحليل الرواتب في سوق العمل السعودي"
    )

    st.markdown("""
    <div style="background:rgba(198,160,60,0.08);border:1px solid rgba(198,160,60,0.2);
    border-radius:8px;padding:0.75rem 1rem;font-size:0.8rem;color:#C6A03C;margin-bottom:1rem;">
    💡 Ranges represent P10 (entry-level), P50 (median market rate), P90 (senior/specialized).
    Estimates based on disclosed job postings and AI-inferred benchmarks.
    </div>
    """, unsafe_allow_html=True)

    salaries_df = load_salaries()

    if salaries_df.empty:
        st.warning("No salary data available yet.")
        return

    # Salary lookup
    section_header("Salary Lookup")
    col1, col2 = st.columns([3, 1])
    with col1:
        search_title = st.text_input("", placeholder="🔍  Search job title e.g. Software Engineer, Doctor...")
    with col2:
        sectors = ['All'] + sorted(salaries_df['sector'].unique().tolist()) if 'sector' in salaries_df.columns else ['All']
        selected_sector = st.selectbox("", sectors, label_visibility="collapsed")

    filtered = salaries_df.copy()
    if search_title:
        filtered = filtered[filtered['job_title'].str.contains(search_title, case=False, na=False)]
    if selected_sector != 'All':
        filtered = filtered[filtered['sector'] == selected_sector]

    if not filtered.empty:
        for _, row in filtered.head(5).iterrows():
            st.markdown(f"""
            <div class="kpi-card" style="margin-bottom:0.75rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
                    <div>
                        <div style="font-size:1rem;font-weight:700;color:#E8EDF5">{row.get('job_title','N/A')}</div>
                        <div style="font-size:0.72rem;color:#6B7FA3;text-transform:uppercase;letter-spacing:0.08em">{row.get('sector','').title()}</div>
                    </div>
                    <div style="display:flex;gap:2rem;">
                        <div style="text-align:center">
                            <div style="font-size:1.1rem;font-weight:700;color:#6B7FA3;font-family:'IBM Plex Mono'">{format_salary(row.get('salary_p10'))}</div>
                            <div style="font-size:0.65rem;color:#4A5A7A;text-transform:uppercase">Entry P10</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:1.3rem;font-weight:800;background:linear-gradient(135deg,#F0C755,#C6A03C);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:'IBM Plex Mono'">{format_salary(row.get('salary_p50'))}</div>
                            <div style="font-size:0.65rem;color:#C6A03C;text-transform:uppercase">Median P50</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:1.1rem;font-weight:700;color:#10B981;font-family:'IBM Plex Mono'">{format_salary(row.get('salary_p90'))}</div>
                            <div style="font-size:0.65rem;color:#4A5A7A;text-transform:uppercase">Senior P90</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Salary Ranges by Sector")

    if 'sector' in salaries_df.columns and 'salary_p50' in salaries_df.columns:
        sector_sal = salaries_df.groupby('sector').agg({
            'salary_p10': 'mean',
            'salary_p50': 'mean',
            'salary_p90': 'mean',
        }).reset_index().round(0)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Entry (P10)', x=sector_sal['sector'].str.title(),
            y=sector_sal['salary_p10'], marker_color='#1E3A5F',
        ))
        fig.add_trace(go.Bar(
            name='Median (P50)', x=sector_sal['sector'].str.title(),
            y=sector_sal['salary_p50'], marker_color='#C6A03C',
        ))
        fig.add_trace(go.Bar(
            name='Senior (P90)', x=sector_sal['sector'].str.title(),
            y=sector_sal['salary_p90'], marker_color='#F0C755',
        ))
        fig = apply_plotly_theme(fig, height=400)
        fig.update_layout(
            barmode='group',
            yaxis_title='SAR per Month',
            xaxis_title=None,
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Full Salary Benchmarks")

    display = salaries_df.copy()
    for col in ['salary_p10', 'salary_p50', 'salary_p90']:
        if col in display.columns:
            display[col] = display[col].apply(
                lambda x: f"SAR {int(x):,}" if pd.notna(x) and x > 0 else "N/A"
            )
    cols = [c for c in ['job_title', 'sector', 'salary_p10', 'salary_p50', 'salary_p90'] if c in display.columns]
    st.dataframe(
        display[cols].rename(columns={
            'job_title': 'Job Title', 'sector': 'Sector',
            'salary_p10': 'Entry (P10)', 'salary_p50': 'Median (P50)', 'salary_p90': 'Senior (P90)',
        }),
        use_container_width=True, hide_index=True,
    )

    st.markdown("""
    <div style="font-size:0.72rem;color:#4A5A7A;margin-top:1rem;">
    ⚠️ Salary estimates are based on market data and AI inference. Actual salaries vary by company,
    experience, and negotiation. Always verify with the employer.
    </div>
    """, unsafe_allow_html=True)