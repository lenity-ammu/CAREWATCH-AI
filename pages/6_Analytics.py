import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from translator import translate_text

# Get selected language
lang = st.session_state.get("language", "English")

st.set_page_config(page_title="Analytics", layout="wide")

st.title("📊"+ translate_text("Hospital Readmission Analytics",lang))

# -----------------------------
# Fake Analytics Data
# -----------------------------

np.random.seed(42)

df = pd.DataFrame({

    "Month":[
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ],

    "Readmissions":[
        120,135,128,150,162,145,
        138,155,149,170,160,175
    ],

    "Average LOS":[
        4.8,5.1,4.9,5.2,5.4,5.0,
        4.7,5.3,5.2,5.5,5.1,5.6
    ]
})

# -----------------------------
# Metrics
# -----------------------------

c1,c2,c3 = st.columns(3)

c1.metric("Total Patients","12,845")
c2.metric("Readmission Rate","18.4%")
c3.metric("Average Stay","5.1 Days")

st.divider()

# -----------------------------
# Line Chart
# -----------------------------

fig1 = px.line(
    df,
    x="Month",
    y="Readmissions",
    markers=True,
    title="Monthly Readmissions"
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# Bar Chart
# -----------------------------

fig2 = px.bar(
    df,
    x="Month",
    y="Average LOS",
    title="Average Length of Stay"
)

st.plotly_chart(fig2, use_container_width=True)