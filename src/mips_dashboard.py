import streamlit as st
import pandas as pd
import plotly.express as px
import os
import psutil


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
    # going to use absolute paths from root of the project, so it works when deployed
    # return pd.read_parquet('../data/cleaned/df_master.parquet')
    current_directory = os.path.dirname(os.path.abspath(__file__))
    path_to_file = os.path.join(current_directory, '..','data','cleaned','df_master.parquet')
    return pd.read_parquet(path_to_file)

df = load_data()
df = df.sample(n=20000,random_state=64)
st.write(f"In-memory size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

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


st.markdown('<h1 style="text-align: center; margin-bottom: 0.5rem;">Merit-Based Incentive Payment System (MIPS) Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size:15px; color:blue;">Explore trends and patterns in MIPS scores </div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size:15px; color:lightblue;">Note: due to Streamlit cloud memory constraints, graphs are drawn based on a sampled subset of providers</div>', unsafe_allow_html=True)
st.divider()


#-- MAIN CONTENT ---
leftbar, vertical_divider, col1, col2 = st.columns([1,0.05,1,3],gap="large")

leftbar.subheader("Filter Providers by:")

states = ['All'] + sorted(df['st'].dropna().unique().tolist())
selected_state = leftbar.selectbox("State", options=states, index=0)
print(f"Selected state: {selected_state}")

specialties = ['All'] + sorted(df['pri_spec'].dropna().unique().tolist())
selected_specialty = leftbar.selectbox("Specialty", options=specialties, index=0)
print(f"Selected specialty: {selected_specialty}")

genders = ['All'] + sorted(df['gndr'].dropna().str.strip().unique().tolist())
selected_gender = leftbar.selectbox("Gender", options=genders, index=0)
print(f"Selected gender: {selected_gender}")

years_exp = ['All'] + sorted(df['years_experience'].dropna().unique().tolist())
selected_years_exp = leftbar.selectbox("Years Experience", options=years_exp, index=0)
print(f"Selected gender: {selected_years_exp}")

med_school = ['All'] + sorted(df['Med_sch'].dropna().unique().tolist())
selected_school = leftbar.selectbox("Medical School", options=med_school, index=0)
print(f"Selected medical school: {selected_school}")

size = ['All'] + sorted(df['num_org_mem'].dropna().unique().tolist())
selected_size = leftbar.selectbox("Practice Size", options=size, index=0)
print(f"Selected size: {selected_size}")

@st.cache_data
def filter_data(df, state, specialty, gender, years_exp, med_school,practice_size):
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
    if practice_size != 'All':
        filtered = filtered[filtered['num_org_mem'] == practice_size]
    return filtered

filtered_df = filter_data(df, selected_state, selected_specialty, selected_gender, selected_years_exp, selected_school, selected_size)

#add in memory usage
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024

st.metric(label="This Dashboard's Memory Usage", value=f"{memory_mb:.2f} MB")


#-- KPI like Metrics ---
def metric_card(label, value, color="#23272b", text_color="#fff", icon=None):
    html = f"""
    <div style="
        background-color: {color};
        padding: 20px 20px 12px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 7px;
        margin-top: 10px;
        min-width: 180px;
        text-align: center;
    ">
        <div style="font-size: 1.1rem; color: #b0b0b0; margin-bottom: 6px;">
            {icon if icon else ""} {label}
        </div>
        <div style="font-size: 2.2rem; font-weight: bold; color: {text_color};">
            {value}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

with vertical_divider:
    st.markdown(
        """
        <div style="height: 100vh; border-left: 2px solid #e0e0e0; margin-left: auto; margin-right: auto;"></div>
        """,
        unsafe_allow_html=True
    )

with col1:
    metric_card("Number of Providers", filtered_df['NPI'].nunique(), color="#f2f6f7", text_color="#23272b")
    metric_card("Average MIPS Score", f"{filtered_df['final_MIPS_score'].mean():.1f}", color="#f2f6f7", text_color="#23272b")
    metric_card("Number of Specialties", filtered_df['pri_spec'].nunique(), color="#f2f6f7", text_color="#23272b")
    metric_card("Males: Females", calculate_gender_distribution(filtered_df), color="#f2f6f7", text_color="#23272b")
    metric_card("Average Years Experience", f"{filtered_df['years_experience'].mean():0.1f}", color="#f2f6f7", text_color="#23272b")
    metric_card("Average Practice Size", f"{filtered_df['num_org_mem'].mean():0.1f}", color="#f2f6f7", text_color="#23272b")

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
    plot_df = filtered_df.sample(n=2000) if len(filtered_df) > 2000 else filtered_df
    fig1 = make_mips_histogram(plot_df, 'final_MIPS_score', "Distribution of Overall Scores",'#25b5b9')
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("- Key Insight: MIPS by design clusters most providers around similar scores (mean 80), so most providers appear the same)")

    #these show the breakdown in MIPS scores by Quality, PI, IA, and Cost
    subcol1, subcol2 = st.columns(2)

    with subcol1:
        plot_df = filtered_df.sample(n=2000) if len(filtered_df) > 2000 else filtered_df
       
        fig2 = make_mips_histogram(plot_df, 'Quality_category_score', "Distribution of Quality Scores",'#b9c3eb')
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = make_mips_histogram(plot_df, 'IA_category_score', "Distribution of Improvement Activities Scores",'#f83a3e')
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("- Key Insight: Improvement Activity scores are all similar, but low (40)")

    with subcol2:
        plot_df = filtered_df.sample(n=2000) if len(filtered_df) > 2000 else filtered_df
        
        fig4 = make_mips_histogram(plot_df, 'PI_category_score', "Distribution of Promoting Interoperability Scores",'#39c3eb')
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("- Key Insight: Almost everyone scored very high (receiving credit often involves just checking boxes)")

        fig5 = make_mips_histogram(plot_df, 'Cost_category_score', "Distribution of Cost Scores",'#fde23a')
        st.plotly_chart(fig5, use_container_width=True)

