import streamlit as st
import pandas as pd
import plotly.express as px

# st.markdown("""
#     <style>
#     div[data-testid="stTabs"] button[role="tab"] p {
#         font-size: 1.8rem !important;
#         padding: 2.5rem 2.1rem !important;
#         min-width: 160px;
#         font-weight: 700 !important;
#         letter-spacing: normal !important;
#     }
#     div[data-testid="stTabs"] div[role="tablist"] {
#         gap: 1rem !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# --- 1. Load Data ---
@st.cache_data
def load_data():
    # Adjust path as needed
    return pd.read_parquet('../data/cleaned/df_master.parquet')

df = load_data()


st.header("Merit-Based Incentive Payment System (MIPS) Dashboard")
st.markdown("Explore trends and patterns in provider MIPS scores")

# Make some tabs

tab1, tab2, tab3 = st.tabs(['Overall MIPS Scores','Quality MIPS','Comparisons'])

with tab1:

    col1, col2 = st.columns(2, gap='large')
    with col1:
        st.markdown(
            f"""
            <div style="background:#f5f7fa; border-radius:18px; padding:32px 36px; margin-bottom:28px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size:2.5rem; color:#888;">Unique Providers</div>
                <div style="font-size:4.6rem; font-weight:700; color:#222;">{df['NPI'].nunique():,}</div>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="background:#f5f7fa; border-radius:18px; padding:32px 36px; margin-bottom:28px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size:2.5rem; color:#888;">Unique Providers</div>
                <div style="font-size:4.6rem; font-weight:700; color:#222;">{df['NPI'].nunique():,}</div>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="background:#f5f7fa; border-radius:18px; padding:32px 36px; margin-bottom:28px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size:2.5rem; color:#888;">Unique Providers</div>
                <div style="font-size:4.6rem; font-weight:700; color:#222;">{df['NPI'].nunique():,}</div>
            </div>
            """, unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="background:#f5f7fa; border-radius:18px; padding:32px 36px; margin-bottom:28px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size:2.5rem; color:#888;">Unique Providers</div>
                <div style="font-size:4.6rem; font-weight:700; color:#222;">{df['NPI'].nunique():,}</div>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="background:#f5f7fa; border-radius:18px; padding:32px 36px; margin-bottom:28px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size:2.5rem; color:#888;">Unique Providers</div>
                <div style="font-size:4.6rem; font-weight:700; color:#222;">{df['NPI'].nunique():,}</div>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="background:#f5f7fa; border-radius:18px; padding:32px 36px; margin-bottom:28px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size:2.5rem; color:#888;">Unique Providers</div>
                <div style="font-size:4.6rem; font-weight:700; color:#222;">{df['NPI'].nunique():,}</div>
            </div>
            """, unsafe_allow_html=True
        )

    tab1.sidebar.title("Filters")


with tab2:
    st.title("Graphs")
    st.write("Visualize the MIPS data")

with tab3:
    st.title("Comparisons")
    st.write("Compare different providers")

