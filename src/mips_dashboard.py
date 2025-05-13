import streamlit as st
import pandas as pd
import plotly.express as px

#--- Page Config ---
st.set_page_config(
    page_title="MIPS Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
# --- 1. Load Data ---
@st.cache_data
def load_data():
    # Adjust path as needed
    return pd.read_parquet('../data/cleaned/df_master.parquet')

df = load_data()

def calculate_gender_distribution(the_df: pd.DataFrame) -> str:
    '''Takes in the master DF and returns the number of unique M and F providers'''
    genders = the_df[['NPI','gndr']]
    #drop duplicate NPIs
    genders = genders.drop_duplicates(subset=['NPI'])
    gender_counts = genders.groupby('gndr')['NPI'].count().reset_index()
    print(f"gender_counts = {gender_counts}")
    try:
        females = gender_counts.iloc[0, 1] / gender_counts['NPI'].sum() * 100
    except IndexError:
        females = 0
    try:
        males = gender_counts.iloc[1, 1] / gender_counts['NPI'].sum() * 100
    except IndexError:
        males = 0
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

specialties = ['All'] + sorted(df['pri_spec'].dropna().unique().tolist())
selected_specialty = sidebar.selectbox("Specialty", options=specialties, index=0)
print(f"Selected specialty: {selected_specialty}")

genders = ['All'] + sorted(df['gndr'].dropna().str.strip().unique().tolist())
selected_gender = sidebar.selectbox("Gender", options=genders, index=0)
print(f"Selected gender: {selected_gender}")

years_exp = ['All'] + sorted(df['years_experience'].dropna().unique().tolist())
selected_years_exp = sidebar.selectbox("Years Experience", options=years_exp, index=0)
print(f"Selected gender: {selected_years_exp}")

med_school = ['All'] + sorted(df['Med_sch'].dropna().unique().tolist())
selected_school = sidebar.selectbox("Medical School", options=med_school, index=0)
print(f"Selected medical school: {selected_school}")

#-- MAIN CONTENT ---
col1, col2 = st.columns([1,3])

@st.cache_data
def filter_data(df, state, specialty, gender, years_exp, med_school):
    filtered = df
    if state != 'All':
        filtered = filtered[filtered['st'] == state]
    if specialty != 'All':
        filtered = filtered[filtered['pri_spec'] == specialty]
    if gender != 'All':
        filtered = filtered[filtered['gndr'].str.strip() == gender]
    if years_exp != 'All':
        filtered = filtered[filtered['years_experience'] == years_exp]
    if med_school != 'All':
        filtered = filtered[filtered['Med_sch'] == med_school]
    return filtered

filtered_df = filter_data(df, selected_state, selected_specialty, selected_gender, selected_years_exp, selected_school)

with col1:
    total_providers = col1.metric(label="Number of Providers", value=filtered_df['NPI'].nunique())
    average_score = col1.metric(label="Average MIPS Score", value=f"{filtered_df['final_MIPS_score'].mean():.1f}")
    total_specialties = col1.metric(label="Number of Specialties", value=filtered_df['pri_spec'].nunique())
    gender_breakdown = col1.metric(label="Males: Females", value=calculate_gender_distribution(filtered_df))
    average_years_experience = col1.metric(label="Average Years Experience", value=f"{filtered_df['years_experience'].mean():0.1f}")

def make_mips_histogram(df, x_col, title, bar_color):
    '''This function creates a histogram of the MIPS scores'''
    fig = px.histogram(
        df,
        x=x_col,
        nbins=110,
        title=title,
        marginal='box',  # Optional: adds a boxplot above
        height=400,
        width=600,
        color_discrete_sequence=[bar_color]  # Use any hex color or named color
    )
    return fig

with col2:
    plot_df = filtered_df.sample(n=150000) if len(filtered_df) > 150000 else filtered_df
    fig1 = make_mips_histogram(plot_df, 'final_MIPS_score', "Distribution of Overall Scores",'#25b5b9')
    st.plotly_chart(fig1, use_container_width=True)

    #these show the breakdown in MIPS scores by Quality, PI, IA, and Cost
    subcol1, subcol2 = st.columns(2)

    with subcol1:
        plot_df = filtered_df.sample(n=50000) if len(filtered_df) > 50000 else filtered_df
       
        fig2 = make_mips_histogram(plot_df, 'Quality_category_score', "Distribution of Quality Scores",'#b9c3eb')
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = make_mips_histogram(plot_df, 'IA_category_score', "Distribution of Improvement Activities Scores",'#f83a3e')
        st.plotly_chart(fig3, use_container_width=True)

    with subcol2:
        plot_df = filtered_df.sample(n=50000) if len(filtered_df) > 50000 else filtered_df
        
        fig4 = make_mips_histogram(plot_df, 'PI_category_score', "Distribution of Promoting Interoperability Scores",'#39c3eb')
        st.plotly_chart(fig4, use_container_width=True)

        fig5 = make_mips_histogram(plot_df, 'Cost_category_score', "Distribution of Cost Scores",'#fde23a')
        st.plotly_chart(fig5, use_container_width=True)