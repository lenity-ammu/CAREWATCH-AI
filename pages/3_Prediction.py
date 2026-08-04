import streamlit as st
import pandas as pd
import numpy as np
import joblib

from translator import translate_text

lang = st.session_state.get("language", "English")

# -----------------------------
# Multilingual Support
# -----------------------------

TEXT = {

    "English":{

        "title":"🩺 Patient Readmission Prediction",

        "button":"🔍 Predict Readmission Risk",

        "high":"🔴 High Risk of 30-Day Readmission",

        "low":"🟢 Low Risk of 30-Day Readmission",

        "prob":"Readmission Probability",

        "result":"Prediction Result"

    },

    "Kannada":{

        "title":"🩺 ರೋಗಿಯ ಮರುದಾಖಲಾತಿ ಮುನ್ಸೂಚನೆ",

        "button":"🔍 ಮುನ್ಸೂಚನೆ",

        "high":"🔴 ಹೆಚ್ಚಿನ ಅಪಾಯ",

        "low":"🟢 ಕಡಿಮೆ ಅಪಾಯ",

        "prob":"ಮರುದಾಖಲಾತಿ ಸಾಧ್ಯತೆ",

        "result":"ಫಲಿತಾಂಶ"

    },

    "Hindi":{

        "title":"🩺 रोगी पुनः भर्ती पूर्वानुमान",

        "button":"🔍 पूर्वानुमान करें",

        "high":"🔴 उच्च जोखिम",

        "low":"🟢 कम जोखिम",

        "prob":"पुनः भर्ती संभावना",

        "result":"परिणाम"

    },

    "Tamil":{

        "title":"🩺 நோயாளி மீள் சேர்க்கை கணிப்பு",

        "button":"🔍 கணிக்கவும்",

        "high":"🔴 அதிக ஆபத்து",

        "low":"🟢 குறைந்த ஆபத்து",

        "prob":"மீள் சேர்க்கை வாய்ப்பு",

        "result":"முடிவு"

    },

    "Telugu":{

        "title":"🩺 రోగి తిరిగి చేర్పు అంచనా",

        "button":"🔍 అంచనా వేయండి",

        "high":"🔴 అధిక ప్రమాదం",

        "low":"🟢 తక్కువ ప్రమాదం",

        "prob":"తిరిగి చేర్పు అవకాశం",

        "result":"ఫలితం"

    },

    "Malayalam":{

        "title":"🩺 രോഗിയുടെ വീണ്ടും പ്രവേശന പ്രവചനം",

        "button":"🔍 പ്രവചിക്കുക",

        "high":"🔴 ഉയർന്ന അപകടസാധ്യത",

        "low":"🟢 കുറഞ്ഞ അപകടസാധ്യത",

        "prob":"വീണ്ടും പ്രവേശന സാധ്യത",

        "result":"ഫലം"

    }

}


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="CareWatch-AI Prediction",
    page_icon="🩺",
    layout="wide"
)

# --------------------------------------------------
# LOAD SAVED MODEL FILES
# --------------------------------------------------

model = joblib.load("model/carewatch_lightgbm_model.pkl")
scaler = joblib.load("model/scaler.pkl")
encoders = joblib.load("model/label_encoders.pkl")
feature_columns = joblib.load("model/feature_columns.pkl")

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🩺 " + translate_text("Patient Readmission Prediction", lang))
st.subheader("AI Powered Hospital Readmission Prediction System")

st.markdown("---")

# ==================================================
# PATIENT DETAILS
# ==================================================

st.header("👤 Patient Information")

col1, col2 = st.columns(2)

with col1:

    age = st.number_input(
        "Age",
        1,
        100,
        50
    )

    gender = st.selectbox(
        "Gender",
        ["M","F","Other"]
    )

    state = st.selectbox(
        "State",
        encoders["state"].classes_
    )

    los_days = st.number_input(
        "Length of Stay",
        1,
        100,
        5
    )

    admit_type = st.selectbox(
        "Admission Type",
        encoders["admit_type"].classes_
    )

    ward_type = st.selectbox(
        "Ward Type",
        encoders["ward_type"].classes_
    )

with col2:

    discharge_type = st.selectbox(
        "Discharge Type",
        encoders["discharge_type"].classes_
    )

    num_procedures = st.number_input(
        "Number of Procedures",
        0,
        20,
        2
    )

    charlson_index = st.number_input(
        "Charlson Index",
        0,
        20,
        1
    )

    prev_admissions = st.number_input(
        "Previous Admissions",
        0,
        20,
        1
    )

    comorbidity_count = st.number_input(
        "Comorbidity Count",
        0,
        20,
        2
    )

st.markdown("---")

# ==================================================
# CLINICAL DETAILS
# ==================================================

st.header("🩸 Clinical Information")

col3, col4 = st.columns(2)

with col3:

    hba1c = st.number_input(
        "HbA1c",
        value=5.5
    )

    creatinine = st.number_input(
        "Creatinine",
        value=1.0
    )

    haemoglobin = st.number_input(
        "Haemoglobin",
        value=13.0
    )

with col4:

    systolic_bp = st.number_input(
        "Systolic BP",
        value=120
    )

    diagnosis_count = st.number_input(
        "Diagnosis Count",
        1,
        20,
        3
    )

    primary_diagnosis = st.selectbox(
        "Primary Diagnosis",
        encoders["primary_diagnosis"].classes_
    )

primary_category = st.selectbox(
    "Primary Category",
    encoders["primary_category"].classes_
)

st.markdown("---")

# ==================================================
# HOSPITAL DETAILS
# ==================================================

st.header("🏥 Hospital Information")

col5, col6 = st.columns(2)

with col5:

    tier = st.selectbox(
        "Hospital Tier",
        encoders["tier"].classes_
    )

    beds = st.number_input(
        "Number of Beds",
        10,
        3000,
        500
    )

with col6:

    teaching = st.checkbox(
        "Teaching Hospital"
    )

st.markdown("---")

# ==================================================
# FINANCIAL DETAILS
# ==================================================

st.header("💰 Financial Information")

col7, col8 = st.columns(2)

with col7:

    insurance_type = st.selectbox(
        "Insurance Type",
        encoders["insurance_type"].classes_
    )

    total_cost_inr = st.number_input(
        "Total Cost (INR)",
        value=50000
    )

    govt_subsidy_inr = st.number_input(
        "Government Subsidy",
        value=10000
    )

with col8:

    out_of_pocket_inr = st.number_input(
        "Out of Pocket Cost",
        value=40000
    )

    cost_category = st.selectbox(
        "Cost Category",
        encoders["cost_category"].classes_
    )

    bpl_card = st.checkbox(
        "BPL Card Holder"
    )

st.markdown("---")

predict = st.button(
    TEXT[lang]["button"],
    use_container_width=True

)

# ==================================================
# PREDICTION
# ==================================================

if predict:

    try:

        # -----------------------------
        # Create Patient Data
        # -----------------------------

        patient = pd.DataFrame({

            "los_days":[los_days],
            "admit_type":[admit_type],
            "ward_type":[ward_type],
            "discharge_type":[discharge_type],
            "num_procedures":[num_procedures],
            "charlson_index":[charlson_index],
            "hba1c":[hba1c],
            "creatinine":[creatinine],
            "haemoglobin":[haemoglobin],
            "systolic_bp":[systolic_bp],
            "age":[age],
            "gender":[gender],
            "state":[state],
            "bpl_card":[bpl_card],
            "insurance_type":[insurance_type],
            "comorbidity_count":[comorbidity_count],
            "prev_admissions":[prev_admissions],
            "total_cost_inr":[total_cost_inr],
            "govt_subsidy_inr":[govt_subsidy_inr],
            "out_of_pocket_inr":[out_of_pocket_inr],
            "cost_category":[cost_category],
            "tier":[tier],
            "beds":[beds],
            "teaching":[teaching],
            "diagnosis_count":[diagnosis_count],
            "primary_diagnosis":[primary_diagnosis],
            "primary_category":[primary_category]

        })

        # -----------------------------
        # Encode Categorical Features
        # -----------------------------

        categorical_columns = [

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

        for col in categorical_columns:

            patient[col] = encoders[col].transform(patient[col])

        # -----------------------------
        # Boolean Conversion
        # -----------------------------

        patient["bpl_card"] = patient["bpl_card"].astype(int)

        patient["teaching"] = patient["teaching"].astype(int)

        # -----------------------------
        # Arrange Columns
        # -----------------------------

        patient = patient[feature_columns]

        # -----------------------------
        # Scale Features
        # -----------------------------

        patient_scaled = scaler.transform(patient)

        # -----------------------------
        # Prediction
        # -----------------------------

        probability = model.predict_proba(patient_scaled)[0][1]
        
        st.session_state.prediction_probability = probability
        
        if probability >= 0.25:
            st.session_state.prediction_result = "High Risk"
        else:
            st.session_state.prediction_result = "Low Risk"

        prediction = int(probability >= 0.25)
        # ===========================
        # Save Prediction Results
        # ===========================

        st.session_state["patient_info"] = {

            "Age": age,
            "Gender": gender,
            "State": state,
            "Admission Type": admit_type,
            "Ward": ward_type,
            "Discharge Type": discharge_type,
            "Primary Diagnosis": primary_diagnosis,
            "Disease Category": primary_category,

            "Length of Stay": los_days,
            "Procedures": num_procedures,
            "Charlson Index": charlson_index,

            "HbA1c": hba1c,
            "Creatinine": creatinine,
            "Haemoglobin": haemoglobin,
            "Systolic BP": systolic_bp,

            "Previous Admissions": prev_admissions,
            "Comorbidity Count": comorbidity_count

        }

        st.session_state["prediction"] = prediction
        st.session_state["probability"] = probability

        
        st.markdown("---")

        st.header(TEXT[lang]["result"])
        if prediction == 1:
            st.error(TEXT[lang]["high"])
        else:
            st.success(TEXT[lang]["low"])

        st.metric(
            TEXT[lang]["prob"],
            f"{probability*100:.2f}%"
)
       
    except Exception as e:

        st.error("Prediction Failed")

        st.exception(e)