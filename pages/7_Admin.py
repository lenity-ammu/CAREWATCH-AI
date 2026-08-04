import streamlit as st
import pandas as pd

from translator import translate_text

# Get selected language
lang = st.session_state.get("language", "English")

st.set_page_config(page_title="Admin", layout="wide")

st.title("👨‍⚕️"+ translate_text(" Admin Dashboard",lang))

st.markdown("### System Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Predictions", "1,245")
c2.metric("Registered Users", "28")
c3.metric("High Risk Cases", "232")
c4.metric("System Status", "Online")

st.divider()

st.subheader("Recent Predictions")

df = pd.DataFrame({

    "Patient ID":[
        "P1001",
        "P1002",
        "P1003",
        "P1004",
        "P1005"
    ],

    "Risk":[
        "Low",
        "High",
        "Low",
        "High",
        "Low"
    ],

    "Probability":[
        "12%",
        "78%",
        "20%",
        "65%",
        "18%"
    ],

    "Status":[
        "Completed",
        "Completed",
        "Completed",
        "Completed",
        "Completed"
    ]

})

st.dataframe(df, use_container_width=True)

st.divider()

st.subheader("System Controls")

col1, col2 = st.columns(2)

with col1:

    if st.button("Refresh System"):

        st.success("System refreshed successfully.")

with col2:

    if st.button("Clear Cache"):

        st.success("Cache cleared successfully.")