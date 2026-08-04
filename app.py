import streamlit as st

st.set_page_config(
    page_title="CareWatch-AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 CareWatch-AI")

st.subheader("AI Powered Hospital Readmission Prediction System")

st.markdown("---")

st.markdown("""
### Welcome to CareWatch-AI

CareWatch-AI is an Artificial Intelligence based Clinical Decision Support System
developed to predict 30-day hospital readmission risk.

### Features

- AI-based Readmission Prediction
- Hospital Analytics Dashboard
- Patient Risk Assessment
- Explainable AI (SHAP)
- PDF Report Generation
- Multi-language Support
- Secure Login System

---
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Hospitals", "150+")

with col2:
    st.metric("Patients", "120,000")

with col3:
    st.metric("AI Accuracy", "82%")

st.markdown("---")

st.success("Project Developed for MSc Dissertation")

