import streamlit as st
from translator import translate_text

lang = st.session_state.get(
    "language",
    "English"
)

st.title("📊"+translate_text(" Hospital Dashboard",lang))

st.markdown("---")

c1,c2,c3,c4=st.columns(4)

c1.metric("Patients","120,000")

c2.metric("Hospitals","150+")

c3.metric("Accuracy","82%")

c4.metric("Model","LightGBM")

st.markdown("---")

st.subheader("Project Overview")

st.info("""

CareWatch-AI predicts whether a patient is likely to be readmitted within 30 days.

Current AI Model

• LightGBM

Threshold = 0.25

Accuracy = 82%

ROC AUC = 0.744

""")

st.markdown("---")

st.subheader("Model Performance")

st.progress(82)

st.success("System Working Normally")

