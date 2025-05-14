import streamlit as st
import pandas as pd
import plotly.express as px
import os
import psutil
import dashboard_utils as dbu


#--- Page Config ---
st.set_page_config(
    page_title="Provider Specialty Opioid Prescribing Patterns Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
# --- 1. Load Data ---
@st.cache_data
def load_data():
    # going to use absolute paths from root of the project, so it works when deployed
    # return pd.read_parquet('../data/cleaned/df_master.parquet')
    current_directory = os.path.dirname(os.path.abspath(__file__))
    path_to_file = os.path.join(current_directory, '..','data','cleaned','opioids_sample.parquet')
    return pd.read_parquet(path_to_file)

df = load_data()
df = df.sample(n=20000,random_state=64)
st.write(f"In-memory size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")


st.markdown('<h1 style="text-align: center; margin-bottom: 0.5rem;">US Opioid Prescribing Patterns by Provider Specialty Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size:15px; color:blue;">Explore geospatial patterns in how narcotics are prescribed</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size:15px; color:lightblue;">Note: data is sampled due to Streamlit cloud memory constraints. Full dataset is 25x larger.</div>', unsafe_allow_html=True)
st.divider()

@st.cache_data
def filter_data(df, state, specialty, gender, years_exp, med_school,practice_size):
    filtered = df
    if state != 'All':
        filtered = filtered[filtered['st'] == state]
    if specialty != 'All':
        filtered = filtered[filtered['Prscrbr_Type'] == specialty]
    # if gender != 'All':
    #     filtered = filtered[filtered['gndr'].str.strip() == gender]
    if years_exp != 'All':
        filtered = filtered[filtered['years_experience'] == years_exp]
    # if med_school != 'All':
    #     filtered = filtered[filtered['Med_sch'] == med_school]
    # if practice_size != 'All':
    #     filtered = filtered[filtered['num_org_mem'] == practice_size]
    return filtered

#--SIDEBAR--
with st.sidebar:
    st.title("Filter by Specialty")

# states = ['All'] + sorted(df['Prscrbr_State_Abrvtn'].dropna().unique().tolist())
# selected_state = st.sidebar.selectbox("State", options=states, index=0)
# print(f"Selected state: {selected_state}")

    specialties = ['All'] + sorted(df['Prscrbr_Type'].dropna().unique().tolist())
    selected_specialty = st.selectbox("Specialty", options=specialties, index=0)
    print(f"Selected specialty: {selected_specialty}")

# genders = ['All'] + sorted(df['gndr'].dropna().str.strip().unique().tolist())
# selected_gender = sidebar.selectbox("Gender", options=genders, index=0)
# print(f"Selected gender: {selected_gender}")

# years_exp = ['All'] + sorted(df['years_experience'].dropna().unique().tolist())
# selected_years_exp = st.sidebar.selectbox("Years Experience", options=years_exp, index=0)
# print(f"Selected gender: {selected_years_exp}")

# med_school = ['All'] + sorted(df['Med_sch'].dropna().unique().tolist())
# selected_school = sidebar.selectbox("Medical School", options=med_school, index=0)
# print(f"Selected medical school: {selected_school}")

# size = ['All'] + sorted(df['num_org_mem'].dropna().unique().tolist())
# selected_size = sidebar.selectbox("Practice Size", options=size, index=0)
# print(f"Selected size: {selected_size}")



    # filtered_df = filter_data(df, selected_state, selected_specialty, selected_gender, selected_years_exp, selected_school, selected_size)
    filtered_df = filter_data(df, None, selected_specialty, None, None, None, None)

    st.divider()

    #add in memory usage
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024

    st.metric(label="This Dashboard's Memory Usage", value=f"{memory_mb:.2f} MB")

#-- MAIN CONTENT ---
col1, col2 = st.columns([1,3],gap="large")


with col1:
    dbu.metric_card("Number of Providers", filtered_df['PRSCRBR_NPI'].nunique(), color="#f2f6f7", text_color="#23272b")
    # dbu.metric_card("Number of Specialties", filtered_df['pri_spec'].nunique(), color="#f2f6f7", text_color="#23272b")
    # dbu.metric_card("Males: Females", calculate_gender_distribution(filtered_df), color="#f2f6f7", text_color="#23272b")
    # dbu.metric_card("Average Years Experience", f"{filtered_df['years_experience'].mean():0.1f}", color="#f2f6f7", text_color="#23272b")
    # dbu.metric_card("Average Practice Size", f"{filtered_df['num_org_mem'].mean():0.1f}", color="#f2f6f7", text_color="#23272b")

# def make_mips_histogram(df, x_col, title, bar_color):
#     '''This function creates a histogram of the MIPS scores'''
#     fig = px.histogram(
#         df,
#         x=x_col,
#         nbins=110,
#         title=title,
#         marginal='box',  # Optional: adds a boxplot above
#         height=300,
#         width=500,
#         color_discrete_sequence=[bar_color]  # Use any hex color or named color
#     )
#     return fig

# with col2:
#     plot_df = filtered_df.sample(n=2000) if len(filtered_df) > 2000 else filtered_df
#     fig1 = make_mips_histogram(plot_df, 'final_MIPS_score', "Distribution of Overall Scores",'#25b5b9')
#     st.plotly_chart(fig1, use_container_width=True)
#     st.markdown("- Key Insight: MIPS by design clusters most providers around similar scores (mean 80), so most providers appear the same)")

#     #these show the breakdown in MIPS scores by Quality, PI, IA, and Cost
#     subcol1, subcol2 = st.columns(2)

#     with subcol1:
#         plot_df = filtered_df.sample(n=2000) if len(filtered_df) > 2000 else filtered_df
       
#         fig2 = make_mips_histogram(plot_df, 'Quality_category_score', "Distribution of Quality Scores",'#b9c3eb')
#         st.plotly_chart(fig2, use_container_width=True)

#         fig3 = make_mips_histogram(plot_df, 'IA_category_score', "Distribution of Improvement Activities Scores",'#f83a3e')
#         st.plotly_chart(fig3, use_container_width=True)
#         st.markdown("- Key Insight: Improvement Activity scores are all similar, but low (40)")

#     with subcol2:
#         plot_df = filtered_df.sample(n=2000) if len(filtered_df) > 2000 else filtered_df
        
#         fig4 = make_mips_histogram(plot_df, 'PI_category_score', "Distribution of Promoting Interoperability Scores",'#39c3eb')
#         st.plotly_chart(fig4, use_container_width=True)
#         st.markdown("- Key Insight: Almost everyone scored very high (receiving credit often involves just checking boxes)")

#         fig5 = make_mips_histogram(plot_df, 'Cost_category_score', "Distribution of Cost Scores",'#fde23a')
#         st.plotly_chart(fig5, use_container_width=True)

