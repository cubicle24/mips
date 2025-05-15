import streamlit as st
import pandas as pd
import plotly.express as px
import os
import psutil
import dashboard_utils as dbu


#--- Page Config ---
st.set_page_config(
    page_title="Opioid Prescribing Patterns Dashboard",
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
            'text': "Opioid Prescribing Rates by Specialty",
            'x': 0.5,  # center title
            'xanchor': 'center',
            'yanchor': 'top',
            'font' : {
                'size' : 36
            }
        }


)
    return fig


#--SIDEBAR--
with st.sidebar:
    st.title("Filter by Specialty")

    specialties = ['All'] + sorted(df['Prscrbr_Type'].dropna().unique().tolist())
    selected_specialty = st.selectbox("Specialty", options=specialties, index=0)
    print(f"Selected specialty: {selected_specialty}")

    themes = ['sunsetdark','reds','aggrnyl','sunset','blackbody','bluered','blues','blugrn','bluyl','brwnyl',
    'bugn','bupu','burg','burgyl','cividis','darkmint','electric','emrld','gnbu','greens','greys','hot',
    'inferno','jet','magenta','magma','mint','orrd','oranges','oryel','peach','pinkyl','plasma','plotly3',
    'pubu','pubugn','purd','purp','purples','purpor','rainbow','rdbu','rdpu','redor',
    'teal','tealgrn','turbo','viridis','ylgn',
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

    st.divider()

    #make the surgical specialties comparison faceted cholorpeth chart
    surgical_specialties_list = ['Obstetrics & Gynecology','Ophthalmology','Otolaryngology','General Surgery','Orthopedic Surgery','Dentist','Urology','Thoracic Surgery','Surgical Oncology','Thoracic Surgery (Cardiothoracic Vascular Surgery) ']
    medical_specialties_list = ['Pain Management','Dermatology','Psychiatry','Addiction Medicine','Emergency Medicine','Neurology','Cardiology','Hospitalist']
    primary_care_specialties_list = ['Internal Medicine','Nurse Practitioner','Family Practice','Physician Assistant']
    surgical_specialties = df[df['Prscrbr_Type'].isin(surgical_specialties_list)]
    medical_specialties = df[df['Prscrbr_Type'].isin(medical_specialties_list)]
    primary_care_specialties = df[df['Prscrbr_Type'].isin(primary_care_specialties_list)]


    def make_choropleth(df,states_col, outcome_of_interest,col_to_facet,color_gradient,title):
        '''makes a facted choloropeth map'''
    # color options: aggrnyl     agsunset    blackbody   bluered     blues       blugrn      bluyl       brwnyl
    # bugn        bupu        burg        burgyl      cividis     darkmint    electric    emrld
    # gnbu        greens      greys       hot         inferno     jet         magenta     magma
    # mint        orrd        oranges     oryel       peach       pinkyl      plasma      plotly3
    # pubu        pubugn      purd        purp        purples     purpor      rainbow     rdbu
    # rdpu        redor       reds        sunset      sunsetdark  teal        tealgrn     turbo
    # viridis     ylgn        ylgnbu      ylorbr      ylorrd      algae       amp         deep
    # dense       gray        haline      ice         matter      solar       speed       tempo
    # thermal     turbid      armyrose    brbg        earth       fall        geyser      prgn
    # piyg        picnic      portland    puor        rdgy        rdylbu      rdylgn      spectral
    # tealrose    temps       tropic      balance     curl        delta       oxy         edge
    # hsv         icefire     phase       twilight    mrybm       mygbm
        fig = px.choropleth(
            df,  # long format: columns = ['state', 'specialty', 'rate']
            locationmode='USA-states',
            locations=states_col,
            color=outcome_of_interest,
            scope='usa',
            facet_col=col_to_facet,
            facet_col_wrap=3,
            # facet_col_spacing=0.02,
            # facet_row_spacing=0.02,
            height=1600,
            width=1200,
            color_continuous_scale=color_gradient,
            title=title
        )

        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,  # center title
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'size': 36
                }
            },
            margin=dict(t=220, l=40, r=40, b=10)  # 🔺 t=top margin in pixels
        )

        return fig

    #compare surgical specialties against each other
    surgical_specialties_map = make_choropleth(surgical_specialties,'Prscrbr_State_Abrvtn',
                                    'Opioid_Prscrbr_Rate','Prscrbr_Type','reds','Surgical Specialties: Opioid Prescribing Rates')
    st.plotly_chart(surgical_specialties_map, use_container_width=True)

    st.divider()
    #compare medical specialties against each other
    medical_specialties_map = make_choropleth(medical_specialties,'Prscrbr_State_Abrvtn',
                                    'Opioid_Prscrbr_Rate','Prscrbr_Type','reds','Medical Specialties: Opioid Prescribing Rates')
    st.plotly_chart(medical_specialties_map, use_container_width=True)

    st.divider()

    #compare primary care against each other
    primary_care_specialties_map = make_choropleth(primary_care_specialties,'Prscrbr_State_Abrvtn',
                                    'Opioid_Prscrbr_Rate','Prscrbr_Type','reds','Primary Care: Opioid Prescribing Rates')
    st.plotly_chart(primary_care_specialties_map, use_container_width=True)

    st.divider()

    st.header("Provider and Patient Characteristics vs. Opioid Prescribing Rate")

    scattercol1, scattercol2 = st.columns(2)
    with scattercol1:

        #scatteprlots of patient and provider factors' impact on prescribing rates
        #look at num_org_mem, telehealth, years of experience, gndr , bene avg risk score vs prescribing rate (scatterplots) #sample b/c it's too big
        # opioids_sample= opioids_raw.sample(n=100000,random_state=64)
        opioids_scatter = df[['PRSCRBR_NPI','Opioid_Prscrbr_Rate','Bene_Avg_Risk_Scre','Bene_Avg_Age','years_experience']]

        print(f"opioids_scatter In-memory size: {opioids_scatter.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print(f"opiods scatter rows: {len(opioids_scatter)}")

        years_exp_scatter = px.scatter(
            opioids_scatter,
            x='years_experience',
            y='Opioid_Prscrbr_Rate',
            opacity=0.1,
            title='Provider Years of Experience vs. Opioid Prescriber Rate',
            labels={
                'years_experience': 'Provider Years of Experience',
                'Opioid_Prscrbr_Rate': 'Opioid Prescriber Rate'
            },
            height=600,
            width=600,
            color_discrete_sequence=['blue']
        )
        st.plotly_chart(years_exp_scatter, use_container_width=True)

        age_chart = px.scatter(
            opioids_scatter,
            x='Bene_Avg_Age',
            y='Opioid_Prscrbr_Rate',
            opacity=0.1,
            title='Patient Age vs. Opioid Prescriber Rate',
            labels={
                'Bene_Avg_Age': 'Average Patient Age',
                'Opioid_Prscrbr_Rate': 'Opioid Prescriber Rate'
            },
            height=600,
            width=600,
            color_discrete_sequence=['blue']
        )
        st.plotly_chart(age_chart, use_container_width=True)

    with scattercol2:
        sickness_chart = px.scatter(
            opioids_scatter,
            x='Bene_Avg_Risk_Scre',
            y='Opioid_Prscrbr_Rate',
            opacity=0.1,
            title='Patient Medical Complexity (Sickness) vs. Opioid Prescriber Rate',
            labels={
                'Bene_Avg_Risk_Scre': 'Patient Medical Complexity (higher is sicker)',
                'Opioid_Prscrbr_Rate': 'Opioid Prescriber Rate'
            },
            height=600,
            width=600,
            color_discrete_sequence=['blue']
        )
        st.plotly_chart(sickness_chart, use_container_width=True)

    st.divider()

    #look at RUCA (population density vs prescribing rate)
    st.header("Provider Practice Location vs. Opioid Prescribing Rate")

    ruca_df = df.groupby('ruca').agg(count=('PRSCRBR_NPI','count'),prescribing_rate=('Opioid_Prscrbr_Rate','mean'))
    ruca_df = ruca_df.reset_index()
    ruca_df

    # Create bar plot
    fig = px.bar(
        ruca_df,
        x='ruca',
        y='prescribing_rate',
        color='prescribing_rate',  # adds gradient coloring
        text='count',              # shows number of prescribers on the bar
        color_continuous_scale='Viridis',  # choose from: 'Viridis', 'Cividis', 'Plasma', 'Blues', etc.
        title='Opioid Prescribing Rate by Population Density',
        labels={
            'ruca': 'RUCA Code',
            'prescribing_rate': 'Mean Opioid Prescribing Rate',
            'count': 'Number of Prescribers'
        }
    )

    # Prettify text on bars
    fig.update_traces(texttemplate='%{text}', textposition='outside')

    # Clean layout
    fig.update_layout(
        yaxis_title='Mean Prescribing Rate %',
        xaxis_title='Population density',
        title_font_size=24,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=10),
        # margin=dict(t=80, b=40, l=60, r=40),
        height=800,
        width=400
    )

    st.plotly_chart(fig, use_container_width=True)