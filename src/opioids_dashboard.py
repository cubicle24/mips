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
# df = df.sample(n=20000,random_state=64)
# st.write(f"In-memory size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")


st.markdown('<h1 style="text-align: center; margin-bottom: 0.5rem;">US Opioid Prescribing Patterns by Provider Specialty Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size:15px; color:blue;">Explore geospatial patterns in how narcotics are prescribed</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-size:15px; color:gray;">Note: data is sampled due to Streamlit cloud memory constraints. Full dataset is 25x larger.</div>', unsafe_allow_html=True)
st.divider()

@st.cache_data
def filter_data(df, state, specialty, gender, years_exp, med_school,practice_size):
    filtered = df
    if state != 'All':
        filtered = filtered[filtered['st'] == state]
    if specialty != 'All':
        filtered = filtered[filtered['Prscrbr_Type'] == specialty]
    if years_exp != 'All':
        filtered = filtered[filtered['years_experience'] == years_exp]
    return filtered

#makes the main map you see (can filter by specialties, zoom in one specialty at a time)
def make_filterable_by_specialty_cholorpeth(df,selected_theme):
    opioids_specialties = df.groupby(['Prscrbr_Type','Prscrbr_State_Abrvtn']).agg(provider_count = ('PRSCRBR_NPI','count'),total_opioid_cost =('Opioid_Tot_Drug_Cst','sum'),prescribing_rate=('Opioid_Prscrbr_Rate','mean'),years_exp=('years_experience','mean'),state=('Prscrbr_State_Abrvtn','count')).reset_index()
    opioids_specialties.Prscrbr_Type.nunique()
    # internists = opioids_specialties[opioids_specialties['Prscrbr_Type'] == 'Internal Medicine']
    print(f"opioids_specialties In-memory size: {opioids_specialties.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    fig = px.choropleth(
        opioids_specialties,
        locations='Prscrbr_State_Abrvtn',
        locationmode='USA-states',
        color='prescribing_rate',
        scope='usa',
        color_continuous_scale=selected_theme,
        hover_name='Prscrbr_State_Abrvtn',
        hover_data={
            'provider_count': True,
            'total_opioid_cost' : ':0.1f',
            'years_exp': ':0.1f',
        },
        title='Opioid Prescribing Rate by Specialty',
        labels={'provider_count': 'Number of Providers', 'prescribing_rate': 'Prescribing Rate','total_opioid_cost': 'Total Opioid Cost','years_exp' : 'Years of Experience'},
        height=800,
        width=1200
    )
    # Center the title
    fig.update_layout(
        title={
            'text': "Opioid Prescribing Rate by Specialty",
            'x': 0.5,  # center title
            'xanchor': 'center',
            'yanchor': 'top'
        }
)
    return fig


#--SIDEBAR--
with st.sidebar:
    st.title("Filter by Specialty")

    specialties = ['All'] + sorted(df['Prscrbr_Type'].dropna().unique().tolist())
    selected_specialty = st.selectbox("Specialty", options=specialties, index=0)
    print(f"Selected specialty: {selected_specialty}")

    themes = ['reds','aggrnyl','sunset','blackbody','bluered','blues','blugrn','bluyl','brwnyl',
    'bugn','bupu','burg','burgyl','cividis','darkmint','electric','emrld','gnbu','greens','greys','hot',
    'inferno','jet','magenta','magma','mint','orrd','oranges','oryel','peach','pinkyl','plasma','plotly3',
    'pubu','pubugn','purd','purp','purples','purpor','rainbow','rdbu','rdpu','redor',
    'sunsetdark','teal','tealgrn','turbo','viridis','ylgn',
    'cividis','darkmint','electric','emrld','gnbu','greens','greys','hot',
    'inferno','jet','magenta','magma','mint','icefire','orrd']

    st.title("Select a Map Theme")
    selected_theme = st.selectbox("Theme", options=themes, index=0)


    # filtered_df = filter_data(df, selected_state, selected_specialty, selected_gender, selected_years_exp, selected_school, selected_size)
    filtered_df = filter_data(df, 'All', selected_specialty, 'All', 'All', 'All', 'All')
    st.divider()

    #add in memory usage
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024

    st.metric(label="This Dashboard's Memory Usage", value=f"{memory_mb:.2f} MB")

#-- MAIN CONTENT ---
col1, col2 = st.columns([1,3],gap="large")


with col1:
    dbu.metric_card("Number of Providers", filtered_df['PRSCRBR_NPI'].nunique(), color="#f2f6f7", text_color="#23272b")
    dbu.metric_card("Average Years Experience", f"{filtered_df['years_experience'].mean():0.1f}", color="#f2f6f7", text_color="#23272b")
    dbu.metric_card("Average Opioid Prescribing Rate", f"{filtered_df['Opioid_Prscrbr_Rate'].mean():0.1f}%", color="#f2f6f7", text_color="#23272b")

with col2:
    # st.dataframe(filtered_df)
    filterable_specialties_map = make_filterable_by_specialty_cholorpeth(filtered_df, selected_theme)
    st.plotly_chart(filterable_specialties_map, use_container_width=True)


