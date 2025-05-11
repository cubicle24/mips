import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. Load Data ---
@st.cache_data
def load_data():
    # Adjust path as needed
    return pd.read_csv('../data/cleaned/df_master.csv', dtype=str)

df = load_data()

# --- 2. Data Cleaning (if needed) ---
# Convert numeric columns
for col in ['Quality_category_score', 'PI_category_score', 'IA_category_score', 'Cost_category_score',
            'final_MIPS_score_without_CPB', 'final_MIPS_score', 'patient_count', 'star_value',
            'five_star_benchmark', 'num_org_mem']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# --- 3. Sidebar Filters ---
st.sidebar.header("Filter Providers")
specialties = ['All'] + sorted(df['prim_spec'].dropna().unique().tolist()) if 'prim_spec' in df.columns else ['All']
states = ['All'] + sorted(df['st'].dropna().unique().tolist()) if 'st' in df.columns else ['All']
measures = ['All'] + sorted(df['measure_title'].dropna().unique().tolist()) if 'measure_title' in df.columns else ['All']

specialty = st.sidebar.selectbox("Specialty", specialties)
state = st.sidebar.selectbox("State", states)
measure = st.sidebar.selectbox("MIPS Measure", measures)

filtered = df.copy()
if specialty != 'All':
    filtered = filtered[filtered['prim_spec'] == specialty]
if state != 'All':
    filtered = filtered[filtered['st'] == state]
if measure != 'All':
    filtered = filtered[filtered['measure_title'] == measure]

# --- 4. Summary Statistics ---
st.title("Provider MIPS Dashboard")
st.markdown("Explore trends and patterns in provider MIPS scores and measures. Use the sidebar to filter.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Unique Providers", filtered['NPI'].nunique())
col2.metric("Unique Measures", filtered['measure_title'].nunique() if 'measure_title' in filtered.columns else 0)
col3.metric("Avg. MIPS Score", f"{filtered['final_MIPS_score'].mean():.1f}" if 'final_MIPS_score' in filtered.columns else "N/A")
col4.metric("Attestation Rate", f"{(filtered['attestation_value']=='Y').mean()*100:.1f}%" if 'attestation_value' in filtered.columns else "N/A")

# --- 5. Top Measures Attested ---
if 'measure_title' in filtered.columns and 'attestation_value' in filtered.columns:
    st.subheader("Top 10 Most Common Measures Attested")
    top_measures = filtered[filtered['attestation_value'] == 'Y']['measure_title'].value_counts().head(10)
    fig1 = px.bar(top_measures, x=top_measures.index, y=top_measures.values, labels={'x':'Measure', 'y':'Count'})
    st.plotly_chart(fig1, use_container_width=True)

# --- 6. Attestation by Specialty ---
if 'prim_spec' in filtered.columns and 'attestation_value' in filtered.columns:
    st.subheader("Attestation Rate by Specialty")
    spec_attest = filtered.groupby('prim_spec')['attestation_value'].apply(lambda x: (x=='Y').mean()*100).sort_values(ascending=False).head(20)
    fig2 = px.bar(spec_attest, x=spec_attest.index, y=spec_attest.values, labels={'x':'Specialty', 'y':'Attestation Rate (%)'})
    st.plotly_chart(fig2, use_container_width=True)

# --- 7. Pie Chart: Attested vs Not Attested ---
if 'attestation_value' in filtered.columns:
    st.subheader("Attestation Distribution")
    pie_data = filtered['attestation_value'].value_counts()
    fig3 = px.pie(names=pie_data.index, values=pie_data.values, title="Attestation Value")
    st.plotly_chart(fig3, use_container_width=True)

# --- 8. Provider Table and Download ---
st.subheader("Provider-Level Data")
st.dataframe(filtered.head(100))
st.download_button("Download Filtered Data", filtered.to_csv(index=False), file_name="filtered_mips.csv")

# --- 9. Outlier Highlighting ---
if 'final_MIPS_score' in filtered.columns:
    st.subheader("Top and Bottom Performers")
    top_providers = filtered.sort_values('final_MIPS_score', ascending=False).drop_duplicates('NPI').head(5)
    bottom_providers = filtered.sort_values('final_MIPS_score', ascending=True).drop_duplicates('NPI').head(5)
    st.markdown("**Top 5 Providers by MIPS Score:**")
    st.dataframe(top_providers[['NPI', 'prim_spec', 'final_MIPS_score']])
    st.markdown("**Bottom 5 Providers by MIPS Score:**")
    st.dataframe(bottom_providers[['NPI', 'prim_spec', 'final_MIPS_score']])

# --- 10. Help/Documentation Sidebar ---
st.sidebar.markdown("---")
st.sidebar.markdown("**How to use this dashboard:**")
st.sidebar.markdown("""
- Use the filters to explore by specialty, state, or measure.
- Click on charts to interact.
- Download filtered data for your own analysis.
- Outliers and trends are highlighted for quick insights.
""")