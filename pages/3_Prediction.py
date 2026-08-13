import os
import json
import hashlib
from datetime import datetime

import joblib
import pandas as pd
import streamlit as st

from auth import require_login, require_role
from blockchain import create_block, verify_blockchain


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | AI Prediction",
    page_icon="🧠",
    layout="wide"
)

# ============================================================
# AUTHENTICATION
# ============================================================

require_login()
require_role("Doctor")


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")


# ============================================================
# LOAD MODEL FILES
# ============================================================

@st.cache_resource
def load_model_files():

    model = joblib.load(
        os.path.join(
            MODEL_DIR,
            "carewatch_lightgbm_model.pkl"
        )
    )

    feature_columns = joblib.load(
        os.path.join(
            MODEL_DIR,
            "feature_columns.pkl"
        )
    )

    label_encoders = joblib.load(
        os.path.join(
            MODEL_DIR,
            "label_encoders.pkl"
        )
    )

    scaler = joblib.load(
        os.path.join(
            MODEL_DIR,
            "scaler.pkl"
        )
    )

    return (
        model,
        feature_columns,
        label_encoders,
        scaler
    )


try:

    model, FEATURE_COLUMNS, LABEL_ENCODERS, SCALER = (
        load_model_files()
    )

except Exception as e:

    st.error("Unable to load the CareWatch-AI prediction model.")
    st.exception(e)
    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_csv(filename):

    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


patients = load_csv("patients.csv")
admissions = load_csv("admissions.csv")
diagnoses = load_csv("diagnoses.csv")
billing = load_csv("billing.csv")
hospitals = load_csv("hospitals.csv")


# ============================================================
# NORMALIZE IDs
# ============================================================

for df, column in [
    (patients, "patient_id"),
    (admissions, "patient_id"),
    (admissions, "admission_id"),
    (diagnoses, "admission_id"),
    (billing, "admission_id"),
    (hospitals, "hospital_id")
]:

    if column in df.columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )


# ============================================================
# HEADER
# ============================================================

st.title("🧠 Patient Readmission Prediction")

st.caption(
    "AI-Based Hospital Readmission Prediction and Clinical Decision Support"
)

st.markdown("---")


# ============================================================
# DATA VALIDATION
# ============================================================

if patients.empty:

    st.error("patients.csv could not be loaded.")
    st.stop()

if admissions.empty:

    st.warning(
        "Admissions data is unavailable. "
        "Prediction may be limited to patient-level information."
    )


# ============================================================
# PATIENT SELECTION
# ============================================================

st.header("👤 Patient Selection")

patient_ids = (
    patients["patient_id"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

patient_ids = sorted(patient_ids)

if not patient_ids:

    st.error("No patients are available.")
    st.stop()


selected_patient_id = st.selectbox(
    "Select Patient",
    patient_ids
)

patient_id = str(selected_patient_id).strip()


# ============================================================
# GET PATIENT
# ============================================================

patient_rows = patients[
    patients["patient_id"] == patient_id
]

if patient_rows.empty:

    st.error("Selected patient was not found.")
    st.stop()

patient = patient_rows.iloc[0]


# ============================================================
# PATIENT ADMISSIONS
# ============================================================

if not admissions.empty:

    patient_admissions = admissions[
        admissions["patient_id"] == patient_id
    ].copy()

else:

    patient_admissions = pd.DataFrame()


# ============================================================
# SORT ADMISSIONS
# ============================================================

if not patient_admissions.empty:

    if "admit_date" in patient_admissions.columns:

        patient_admissions["admit_date"] = pd.to_datetime(
            patient_admissions["admit_date"],
            errors="coerce"
        )

        patient_admissions = patient_admissions.sort_values(
            "admit_date",
            ascending=False
        )


# ============================================================
# LATEST ADMISSION
# ============================================================

if not patient_admissions.empty:

    latest_admission = patient_admissions.iloc[0]

else:

    latest_admission = pd.Series(dtype=object)


# ============================================================
# PATIENT INFORMATION
# ============================================================

st.markdown("---")

st.header("🏥 Electronic Health Record")

st.caption(
    "Patient information is automatically retrieved "
    "from the CareWatch-AI EHR datasets."
)

st.subheader("👤 Patient Information")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Patient ID",
        patient_id
    )

with c2:
    st.metric(
        "Age",
        patient.get("age", "N/A")
    )

with c3:
    st.metric(
        "Gender",
        patient.get("gender", "N/A")
    )

with c4:
    st.metric(
        "State",
        patient.get("state", "N/A")
    )

with c5:
    st.metric(
        "Comorbidities",
        patient.get("comorbidity_count", "N/A")
    )


c1, c2, c3 = st.columns(3)

with c1:
    st.info(
        f"**BPL Card:** {patient.get('bpl_card', 'N/A')}"
    )

with c2:
    st.info(
        f"**Insurance:** {patient.get('insurance_type', 'N/A')}"
    )

with c3:
    st.info(
        f"**Previous Admissions:** "
        f"{patient.get('prev_admissions', 'N/A')}"
    )


# ============================================================
# ADMISSION INFORMATION
# ============================================================

if patient_admissions.empty:

    st.info(
        "No admission history was found for this patient. "
        "Prediction can still be performed using available patient information."
    )

else:

    st.subheader("🏥 Latest Admission")

    admission_id = latest_admission.get(
        "admission_id",
        "N/A"
    )

    st.write(
        f"**Admission ID:** {admission_id}"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Admission Type",
            latest_admission.get(
                "admit_type",
                "N/A"
            )
        )

    with c2:

        st.metric(
            "Ward Type",
            latest_admission.get(
                "ward_type",
                "N/A"
            )
        )

    with c3:

        st.metric(
            "Discharge Type",
            latest_admission.get(
                "discharge_type",
                "N/A"
            )
        )

    with c4:

        st.metric(
            "Length of Stay",
            latest_admission.get(
                "los_days",
                "N/A"
            )
        )


# ============================================================
# DIAGNOSIS INFORMATION
# ============================================================

patient_diagnoses = pd.DataFrame()

if (
    not patient_admissions.empty
    and not diagnoses.empty
    and "admission_id" in diagnoses.columns
):

    admission_ids = (
        patient_admissions["admission_id"]
        .astype(str)
        .tolist()
    )

    patient_diagnoses = diagnoses[
        diagnoses["admission_id"].astype(str).isin(
            admission_ids
        )
    ].copy()


# ============================================================
# PRIMARY DIAGNOSIS
# ============================================================

primary_diagnosis = "Unknown"
primary_category = "Unknown"
diagnosis_count = 0

if not patient_diagnoses.empty:

    diagnosis_count = len(patient_diagnoses)

    if "diag_rank" in patient_diagnoses.columns:

        ranked = patient_diagnoses.copy()

        ranked["_rank"] = pd.to_numeric(
            ranked["diag_rank"],
            errors="coerce"
        )

        ranked = ranked.sort_values(
            "_rank",
            ascending=True
        )

        primary_row = ranked.iloc[0]

    else:

        primary_row = patient_diagnoses.iloc[0]

    primary_diagnosis = str(
        primary_row.get(
            "icd10_code",
            "Unknown"
        )
    )

    primary_category = str(
        primary_row.get(
            "diag_category",
            "Unknown"
        )
    )

else:

    if not patient_admissions.empty:

        st.info(
            "No diagnosis records were found for the latest admission."
        )


# ============================================================
# HOSPITAL INFORMATION
# ============================================================

hospital_tier = "Unknown"
hospital_beds = 0
hospital_teaching = False

hospital_id = None

if not patient_admissions.empty:

    hospital_id = latest_admission.get(
        "hospital_id"
    )

if (
    hospital_id is not None
    and not hospitals.empty
    and "hospital_id" in hospitals.columns
):

    hospital_rows = hospitals[
        hospitals["hospital_id"].astype(str)
        == str(hospital_id)
    ]

    if not hospital_rows.empty:

        hospital = hospital_rows.iloc[0]

        hospital_tier = hospital.get(
            "tier",
            "Unknown"
        )

        hospital_beds = hospital.get(
            "beds",
            0
        )

        hospital_teaching = hospital.get(
            "teaching",
            False
        )


# ============================================================
# BILLING INFORMATION
# ============================================================

total_cost = 0.0
govt_subsidy = 0.0
out_of_pocket = 0.0
cost_category = "Unknown"

patient_billing = pd.DataFrame()

if (
    not patient_admissions.empty
    and not billing.empty
    and "admission_id" in billing.columns
):

    admission_ids = (
        patient_admissions["admission_id"]
        .astype(str)
        .tolist()
    )

    patient_billing = billing[
        billing["admission_id"].astype(str).isin(
            admission_ids
        )
    ].copy()

if not patient_billing.empty:

    if "total_cost_inr" in patient_billing.columns:

        total_cost = pd.to_numeric(
            patient_billing["total_cost_inr"],
            errors="coerce"
        ).fillna(0).sum()

    if "govt_subsidy_inr" in patient_billing.columns:

        govt_subsidy = pd.to_numeric(
            patient_billing["govt_subsidy_inr"],
            errors="coerce"
        ).fillna(0).sum()

    if "out_of_pocket_inr" in patient_billing.columns:

        out_of_pocket = pd.to_numeric(
            patient_billing["out_of_pocket_inr"],
            errors="coerce"
        ).fillna(0).sum()

    if "cost_category" in patient_billing.columns:

        cost_category = str(
            patient_billing.iloc[0].get(
                "cost_category",
                "Unknown"
            )
        )


# ============================================================
# AI PREDICTION INPUTS
# ============================================================

st.markdown("---")

st.header("🤖 AI Readmission Risk Prediction")

st.caption(
    "Values are pre-filled from the patient's EHR. "
    "The doctor may review them before running the prediction."
)


# ============================================================
# SAFE VALUE FUNCTIONS
# ============================================================

def safe_float(value, default=0.0):

    try:

        number = float(value)

        if pd.isna(number):
            return float(default)

        return number

    except Exception:

        return float(default)


def safe_int(value, default=0):

    try:

        number = int(float(value))

        return number

    except Exception:

        return int(default)


def safe_bool(value):

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in [
        "true",
        "1",
        "yes",
        "y",
        "t"
    ]


# ============================================================
# DEFAULT VALUES
# ============================================================

default_age = safe_int(
    patient.get("age", 50),
    50
)

default_gender = str(
    patient.get("gender", "M")
)

default_state = str(
    patient.get("state", "Unknown")
)

default_bpl = safe_bool(
    patient.get("bpl_card", False)
)

default_insurance = str(
    patient.get(
        "insurance_type",
        "Unknown"
    )
)

default_comorbidity = safe_int(
    patient.get(
        "comorbidity_count",
        0
    )
)

default_previous = safe_int(
    patient.get(
        "prev_admissions",
        0
    )
)


# ============================================================
# ADMISSION DEFAULTS
# ============================================================

default_los = 1
default_admit_type = "Unknown"
default_ward_type = "Unknown"
default_discharge_type = "Unknown"
default_procedures = 0
default_charlson = 0.0
default_hba1c = 0.0
default_creatinine = 0.0
default_haemoglobin = 0.0
default_sbp = 120.0

if not patient_admissions.empty:

    default_los = safe_int(
        latest_admission.get(
            "los_days",
            1
        ),
        1
    )

    default_admit_type = str(
        latest_admission.get(
            "admit_type",
            "Unknown"
        )
    )

    default_ward_type = str(
        latest_admission.get(
            "ward_type",
            "Unknown"
        )
    )

    default_discharge_type = str(
        latest_admission.get(
            "discharge_type",
            "Unknown"
        )
    )

    default_procedures = safe_int(
        latest_admission.get(
            "num_procedures",
            0
        )
    )

    default_charlson = safe_float(
        latest_admission.get(
            "charlson_index",
            0
        )
    )

    default_hba1c = safe_float(
        latest_admission.get(
            "hba1c",
            0
        )
    )

    default_creatinine = safe_float(
        latest_admission.get(
            "creatinine",
            0
        )
    )

    default_haemoglobin = safe_float(
        latest_admission.get(
            "haemoglobin",
            0
        )
    )

    default_sbp = safe_float(
        latest_admission.get(
            "systolic_bp",
            120
        ),
        120
    )


# ============================================================
# CLINICAL INPUTS
# ============================================================

c1, c2, c3 = st.columns(3)

with c1:

    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=int(default_age),
        step=1
    )

with c2:

    gender = st.text_input(
        "Gender",
        value=default_gender
    )

with c3:

    state = st.text_input(
        "State",
        value=default_state
    )


c1, c2, c3 = st.columns(3)

with c1:

    los_days = st.number_input(
        "Length of Stay",
        min_value=0,
        max_value=365,
        value=int(default_los),
        step=1
    )

with c2:

    admit_type = st.text_input(
        "Admission Type",
        value=default_admit_type
    )

with c3:

    ward_type = st.text_input(
        "Ward Type",
        value=default_ward_type
    )


c1, c2, c3 = st.columns(3)

with c1:

    discharge_type = st.text_input(
        "Discharge Type",
        value=default_discharge_type
    )

with c2:

    num_procedures = st.number_input(
        "Number of Procedures",
        min_value=0,
        max_value=100,
        value=int(default_procedures),
        step=1
    )

with c3:

    charlson_index = st.number_input(
        "Charlson Index",
        min_value=0.0,
        max_value=50.0,
        value=float(default_charlson),
        step=0.1
    )


c1, c2, c3 = st.columns(3)

with c1:

    prev_admissions = st.number_input(
        "Previous Admissions",
        min_value=0,
        max_value=100,
        value=int(default_previous),
        step=1
    )

with c2:

    comorbidity_count = st.number_input(
        "Comorbidity Count",
        min_value=0,
        max_value=50,
        value=int(default_comorbidity),
        step=1
    )

with c3:

    diagnosis_count_input = st.number_input(
        "Diagnosis Count",
        min_value=0,
        max_value=100,
        value=int(diagnosis_count),
        step=1
    )


# ============================================================
# CLINICAL LABS
# ============================================================

st.subheader("🩸 Clinical Information")

c1, c2, c3, c4 = st.columns(4)

with c1:

    hba1c = st.number_input(
        "HbA1c",
        min_value=0.0,
        max_value=30.0,
        value=float(default_hba1c),
        step=0.1
    )

with c2:

    creatinine = st.number_input(
        "Creatinine",
        min_value=0.0,
        max_value=30.0,
        value=float(default_creatinine),
        step=0.1
    )

with c3:

    haemoglobin = st.number_input(
        "Haemoglobin",
        min_value=0.0,
        max_value=30.0,
        value=float(default_haemoglobin),
        step=0.1
    )

with c4:

    systolic_bp = st.number_input(
        "Systolic BP",
        min_value=0.0,
        max_value=300.0,
        value=float(default_sbp),
        step=1.0
    )


c1, c2, c3 = st.columns(3)

with c1:

    primary_diagnosis_input = st.text_input(
        "Primary Diagnosis",
        value=primary_diagnosis
    )

with c2:

    primary_category_input = st.text_input(
        "Primary Category",
        value=primary_category
    )

with c3:

    st.metric(
        "Diagnosis Count",
        int(diagnosis_count_input)
    )


# ============================================================
# HOSPITAL INFORMATION
# ============================================================

st.subheader("🏥 Hospital Information")

c1, c2, c3 = st.columns(3)

with c1:

    hospital_tier_input = st.text_input(
        "Hospital Tier",
        value=str(hospital_tier)
    )

with c2:

    hospital_beds_input = st.number_input(
        "Number of Beds",
        min_value=0,
        max_value=10000,
        value=int(safe_int(hospital_beds)),
        step=1
    )

with c3:

    teaching_input = st.checkbox(
        "Teaching Hospital",
        value=safe_bool(hospital_teaching)
    )


# ============================================================
# FINANCIAL INFORMATION
# ============================================================

st.subheader("💰 Financial Information")

insurance_type = st.text_input(
    "Insurance Type",
    value=default_insurance
)

c1, c2, c3 = st.columns(3)

with c1:

    total_cost_inr = st.number_input(
        "Total Cost (INR)",
        min_value=0.0,
        max_value=100000000.0,
        value=float(total_cost),
        step=100.0
    )

with c2:

    govt_subsidy_inr = st.number_input(
        "Government Subsidy (INR)",
        min_value=0.0,
        max_value=100000000.0,
        value=float(govt_subsidy),
        step=100.0
    )

with c3:

    out_of_pocket_inr = st.number_input(
        "Out-of-Pocket Cost (INR)",
        min_value=0.0,
        max_value=100000000.0,
        value=float(out_of_pocket),
        step=100.0
    )


cost_category_input = st.text_input(
    "Cost Category",
    value=str(cost_category)
)

bpl_card_input = st.checkbox(
    "BPL Card Holder",
    value=default_bpl
)


# ============================================================
# BUILD RAW FEATURE DATAFRAME
# ============================================================

raw_features = {

    "los_days": float(los_days),

    "admit_type": str(admit_type),

    "ward_type": str(ward_type),

    "discharge_type": str(discharge_type),

    "num_procedures": float(num_procedures),

    "charlson_index": float(charlson_index),

    "hba1c": float(hba1c),

    "creatinine": float(creatinine),

    "haemoglobin": float(haemoglobin),

    "systolic_bp": float(systolic_bp),

    "age": float(age),

    "gender": str(gender),

    "state": str(state),

    "bpl_card": bool(bpl_card_input),

    "insurance_type": str(insurance_type),

    "comorbidity_count": float(comorbidity_count),

    "prev_admissions": float(prev_admissions),

    "total_cost_inr": float(total_cost_inr),

    "govt_subsidy_inr": float(govt_subsidy_inr),

    "out_of_pocket_inr": float(out_of_pocket_inr),

    "cost_category": str(cost_category_input),

    "tier": str(hospital_tier_input),

    "beds": float(hospital_beds_input),

    "teaching": bool(teaching_input),

    "diagnosis_count": float(diagnosis_count_input),

    "primary_diagnosis": str(primary_diagnosis_input),

    "primary_category": str(primary_category_input)
}


# ============================================================
# ENCODING
# ============================================================

def encode_value(column, value):

    if column not in LABEL_ENCODERS:

        return value

    encoder = LABEL_ENCODERS[column]

    value_string = str(value)

    classes = list(
        getattr(
            encoder,
            "classes_",
            []
        )
    )

    if value_string in classes:

        return int(
            encoder.transform(
                [value_string]
            )[0]
        )

    # Unknown categorical value:
    # use first known class instead of crashing

    if len(classes) > 0:

        fallback = classes[0]

        return int(
            encoder.transform(
                [fallback]
            )[0]
        )

    return 0


# ============================================================
# PREPARE MODEL INPUT
# ============================================================

def prepare_model_input():

    df = pd.DataFrame(
        [raw_features]
    )

    # Ensure every expected feature exists

    for feature in FEATURE_COLUMNS:

        if feature not in df.columns:

            df[feature] = 0

    # Keep exact model feature order

    df = df[
        FEATURE_COLUMNS
    ].copy()

    # Encode categorical columns

    for column in LABEL_ENCODERS.keys():

        if column in df.columns:

            df[column] = df[column].apply(
                lambda x: encode_value(
                    column,
                    x
                )
            )

    # Convert remaining columns to numeric

    for column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.fillna(0)

    return df


# ============================================================
# PREDICTION BUTTON
# ============================================================

st.markdown("---")

predict_clicked = st.button(
    "🧠 Run 30-Day Readmission Prediction",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN PREDICTION
# ============================================================

if predict_clicked:

    try:

        model_input = prepare_model_input()

        # ----------------------------------------------------
        # SCALE
        # ----------------------------------------------------

        try:

            scaled_input = SCALER.transform(
                model_input
            )

        except Exception:

            scaled_input = model_input.values

        # ----------------------------------------------------
        # PREDICT
        # ----------------------------------------------------

        if hasattr(
            model,
            "predict_proba"
        ):

            probabilities = model.predict_proba(
                scaled_input
            )

            probability = float(
                probabilities[0][1]
            )

        else:

            prediction = model.predict(
                scaled_input
            )

            probability = float(
                prediction[0]
            )

        # ----------------------------------------------------
        # NORMALIZE PROBABILITY
        # ----------------------------------------------------

        if probability > 1:

            probability = probability / 100.0

        probability = max(
            0.0,
            min(
                1.0,
                probability
            )
        )

        percentage = probability * 100.0

        # ----------------------------------------------------
        # RISK CLASSIFICATION
        # ----------------------------------------------------

        if percentage >= 60:

            risk_level = "High"
            risk_icon = "🔴"

            clinical_summary = (
                "The AI model indicates a higher risk "
                "of 30-day hospital readmission. "
                "Closer clinical monitoring and "
                "appropriate follow-up may be required."
            )

            recommendations = [
                "Discuss the assessment with the treating doctor.",
                "Consider closer clinical monitoring.",
                "Review discharge and follow-up planning.",
                "Monitor relevant clinical risk factors."
            ]

        elif percentage >= 30:

            risk_level = "Moderate"
            risk_icon = "🟠"

            clinical_summary = (
                "The AI model indicates a moderate risk "
                "of 30-day hospital readmission. "
                "Additional clinical monitoring may be appropriate."
            )

            recommendations = [
                "Discuss the assessment with the treating doctor.",
                "Attend scheduled follow-up appointments.",
                "Continue regular health monitoring."
            ]

        else:

            risk_level = "Low"
            risk_icon = "🟢"

            clinical_summary = (
                "The AI model indicates a lower risk "
                "of 30-day hospital readmission."
            )

            recommendations = [
                "Continue following the healthcare plan.",
                "Attend scheduled follow-up appointments.",
                "Maintain regular health monitoring."
            ]


        # ====================================================
        # SAVE PREDICTION CSV
        # ====================================================

        prediction_file = os.path.join(
            BASE_DIR,
            "prediction_results.csv"
        )

        prediction_record = {

            "timestamp":
                datetime.now().isoformat(),

            "patient_id":
                patient_id,

            "risk_level":
                risk_level,

            "readmission_probability":
                round(
                    percentage,
                    4
                ),

            "clinical_summary":
                clinical_summary
        }

        prediction_df = pd.DataFrame(
            [prediction_record]
        )

        if os.path.exists(
            prediction_file
        ):

            try:

                old_predictions = pd.read_csv(
                    prediction_file
                )

                prediction_df = pd.concat(
                    [
                        old_predictions,
                        prediction_df
                    ],
                    ignore_index=True
                )

            except Exception:
                pass

        prediction_df.to_csv(
            prediction_file,
            index=False
        )


        # ====================================================
        # SESSION STATE
        # ====================================================

        st.session_state[
            "last_prediction"
        ] = prediction_record

        st.session_state[
            "selected_patient_id"
        ] = patient_id

        st.session_state[
            "patient_id"
        ] = patient_id


        # ====================================================
        # BLOCKCHAIN RECORD
        # ====================================================

        blockchain_success = False
        blockchain_message = ""

        try:

            blockchain_record = {

                "patient_id":
                    patient_id,

                "risk_level":
                    risk_level,

                "readmission_probability":
                    round(
                        percentage,
                        4
                    ),

                "clinical_summary":
                    clinical_summary,

                "recommendations":
                    recommendations,

                "timestamp":
                    datetime.now().isoformat(),

                "created_by":
                    st.session_state.get(
                        "username",
                        "doctor"
                    )
            }

            block = create_block(
                "AI_PREDICTION",
                blockchain_record
            )

            blockchain_success = True

            blockchain_message = (
                f"Blockchain block {block.get('block_index')} "
                "created successfully."
            )

        except Exception as blockchain_error:

            blockchain_message = str(
                blockchain_error
            )


        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        st.markdown("---")

        st.header("📊 Prediction Result")

        st.success(
            "Prediction saved successfully."
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Risk Level",
                risk_level
            )

        with c2:

            st.metric(
                "Readmission Probability",
                f"{percentage:.2f}%"
            )

        with c3:

            st.metric(
                "Patient ID",
                patient_id
            )


        st.markdown(
            f"# {risk_icon} {risk_level} Risk"
        )


        # ====================================================
        # CLINICAL SUMMARY
        # ====================================================

        st.subheader(
            "🧠 Clinical Summary"
        )

        st.info(
            clinical_summary
        )


        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        st.subheader(
            "💡 Recommendations"
        )

        for recommendation in recommendations:

            st.write(
                f"✅ {recommendation}"
            )


        # ====================================================
        # BLOCKCHAIN RESULT
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🔗 Blockchain Audit Record"
        )

        if blockchain_success:

            st.success(
                blockchain_message
            )

            try:

                verification = verify_blockchain()

                if isinstance(
                    verification,
                    tuple
                ):

                    valid, message = verification

                else:

                    valid = bool(
                        verification
                    )

                    message = (
                        "Blockchain verification completed."
                    )

                if valid:

                    st.success(
                        f"✓ {message}"
                    )

                else:

                    st.error(
                        f"✗ {message}"
                    )

            except Exception as verification_error:

                st.warning(
                    "Blockchain record was created, "
                    "but verification could not be completed."
                )

                st.caption(
                    str(verification_error)
                )

        else:

            st.warning(
                "Prediction was saved, but the blockchain "
                "record could not be created."
            )

            st.code(
                blockchain_message
            )


        # ====================================================
        # NAVIGATION
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📋 Continue Clinical Workflow"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.page_link(
                "pages/11_EHR.py",
                label="📋 Open EHR",
                use_container_width=True
            )

        with c2:

            st.page_link(
                "pages/4_SHAP_Explainability.py",
                label="🔬 Open SHAP / XAI",
                use_container_width=True
            )

        with c3:

            st.page_link(
                "pages/12_Blockchain.py",
                label="🔗 Blockchain Audit",
                use_container_width=True
            )


    # ========================================================
    # PREDICTION ERROR
    # ========================================================

    except Exception as prediction_error:

        st.error(
            "Prediction failed."
        )

        st.exception(
            prediction_error
        )