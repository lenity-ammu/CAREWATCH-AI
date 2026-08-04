import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt

from translator import translate_text

# Get selected language
lang = st.session_state.get("language", "English")


st.set_page_config(page_title="SHAP Explainability", page_icon="🧠", layout="wide")

st.title("🧠"+ translate_text(" AI Explainability (SHAP)",lang))
st.markdown("Understand why the AI predicted the patient's readmission risk.")

# -----------------------------
# Load Model
# -----------------------------
model = joblib.load("model/carewatch_lightgbm_model.pkl")
scaler = joblib.load("model/scaler.pkl")
label_encoders = joblib.load("model/label_encoders.pkl")
feature_columns = joblib.load("model/feature_columns.pkl")

# -----------------------------
# Sample Patient Data
# -----------------------------
sample = {
    "los_days":5,
    "admit_type":"Emergency",
    "ward_type":"General",
    "discharge_type":"Recovered",
    "num_procedures":2,
    "charlson_index":1,
    "hba1c":5.5,
    "creatinine":1.0,
    "haemoglobin":13,
    "systolic_bp":120,
    "age":50,
    "gender":"M",
    "state":"Karnataka",
    "bpl_card":1,
    "insurance_type":"Ayushman",
    "comorbidity_count":2,
    "prev_admissions":1,
    "total_cost_inr":50000,
    "govt_subsidy_inr":10000,
    "out_of_pocket_inr":40000,
    "cost_category":"Lab",
    "tier":"tier1",
    "beds":500,
    "teaching":1,
    "diagnosis_count":3,
    "primary_diagnosis":"Type 2 diabetes mellitus",
    "primary_category":"Endocrine"
}

df = pd.DataFrame([sample])

# -----------------------------
# Encode Categorical Columns
# -----------------------------
categorical = [
    "admit_type",
    "ward_type",
    "discharge_type",
    "gender",
    "state",
    "insurance_type",
    "cost_category",
    "tier",
    "primary_diagnosis",
    "primary_category"
]

for col in categorical:
    df[col] = label_encoders[col].transform(df[col])

# -----------------------------
# Scale Numeric Features
# -----------------------------
numeric = [
    "los_days",
    "num_procedures",
    "charlson_index",
    "hba1c",
    "creatinine",
    "haemoglobin",
    "systolic_bp",
    "age",
    "comorbidity_count",
    "prev_admissions",
    "total_cost_inr",
    "govt_subsidy_inr",
    "out_of_pocket_inr",
    "beds",
    "diagnosis_count"
]

# Arrange columns
df = df[feature_columns]

# Scale ALL features
df_scaled = scaler.transform(df)

# -----------------------------
# Prediction
# -----------------------------
prob = model.predict_proba(df_scaled)[0][1]

st.metric("Predicted Readmission Risk", f"{prob:.2%}")

# -----------------------------
# SHAP Values
# -----------------------------
explainer = shap.TreeExplainer(model)

shap_values = explainer.shap_values(df_scaled)

st.subheader("Feature Importance")

fig, ax = plt.subplots(figsize=(10,6))

shap.summary_plot(
    shap_values,
    df,
    show=False
)

st.pyplot(fig, clear_figure=True)

st.subheader("Waterfall Explanation")
st.markdown("### 📝 Explanation")

st.info("""
- 🔴 Red bars increase the patient's readmission risk.
- 🔵 Blue bars decrease the patient's readmission risk.
- Larger bars have a stronger influence on the prediction.
- The final value represents the AI model's predicted risk for this patient.
""")

fig2 = plt.figure(figsize=(10,6))

shap.plots.waterfall(
    shap.Explanation(
        values=shap_values[0],
        base_values=explainer.expected_value,
        data=df_scaled[0],
        feature_names=feature_columns
    ),
    show=False
)

st.pyplot(fig2)
