import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. Load Data ---
@st.cache_data
def load_data():
    # Adjust path as needed
    return pd.read_parquet('../data/cleaned/df_master.parquet')

df = load_data()


#--- Page Config ---
st.set_page_config(
    page_title="MIPS Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def calculate_gender_distribution(df: pd.DataFrame) -> str:
    '''Takes in the master DF and returns the number of unique M and F providers'''
    genders = df[['NPI','gndr']]
    #drop duplicate NPIs
    genders = genders.drop_duplicates(subset=['NPI'])
    gender_counts = genders.groupby('gndr')['NPI'].count().reset_index()
    # gender_counts.columns = ['Gender', 'Count']
    females = gender_counts.iloc[0, 1] / gender_counts['NPI'].sum() * 100
    males = gender_counts.iloc[1, 1] / gender_counts['NPI'].sum() * 100
    return (f"{males:.1f}% : {females:.1f}%")


st.header("Merit-Based Incentive Payment System (MIPS) Dashboard")
st.markdown("Explore trends and patterns in provider MIPS scores")
st.divider()

#-- SIDEBAR ---
sidebar = st.sidebar
sidebar.title("Filter Providers by:")
states = ['All'] + sorted(df['st'].dropna().unique().tolist())

selected_state = sidebar.selectbox("State", options=states, index=0)
print(f"Selected state: {selected_state}")

#-- MAIN CONTENT ---
col1, col2 = st.columns([1,3])

if selected_state == 'All':
    filtered_df = df.copy()
else:
    filtered_df = df[df['st'] == selected_state].copy()

with col1:

    total_providers = col1.metric(label="Number of Providers", value=filtered_df['NPI'].nunique())
    average_score = col1.metric(label="Average MIPS Score", value=f"{filtered_df['final_MIPS_score'].mean():.1f}")
    total_specialties = col1.metric(label="Number of Specialties", value=filtered_df['pri_spec'].nunique())
    gender_breakdown = col1.metric(label="Males: Females", value=calculate_gender_distribution(filtered_df))

with col2:
    fig = px.histogram(
        filtered_df,
        x='final_MIPS_score',
        nbins=110,
        title="Distribution of MIPS Scores",
        marginal='box',  # Optional: adds a boxplot above
        height=1000,
        width=700
    )
    st.plotly_chart(fig, use_container_width=True)
