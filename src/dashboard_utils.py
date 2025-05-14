import streamlit as st
import pandas as pd
import plotly.express as px

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

def make_histogram(df, x_col, title, bar_color):
    '''This function creates a histogram of the 'x' variable'''
    fig = px.histogram(
        df,
        x=x_col,
        nbins=110,
        title=title,
        marginal='box',  # Optional: adds a boxplot above
        height=300,
        width=500,
        color_discrete_sequence=[bar_color]  # Use any hex color or named color
    )
    return fig