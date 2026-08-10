import streamlit as st
import pandas as pd
import joblib
import os

from auth import require_role
from translator import translate_text


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareWatch-AI | Prediction",
    page_icon="🩺",
    layout="wide"
)


# =========================================================
# ACCESS
# =========================================================

require_role(["Doctor"])


# =========================================================
# LANGUAGE
# =========================================================

lang = st.session_state.get("language", "English")

TEXT = {

    "English": {
        "title": "🩺 Patient Readmission Prediction",
        "button": "🔍 Predict Readmission Risk",
        "high": "🔴 High Risk of 30-Day Readmission",
        "low": "🟢 Low Risk of 30-Day Readmission",
        "prob": "Readmission Probability",
        "result": "Prediction Result",
        "patient": "Patient ID",
        "saved": "Prediction saved successfully.",
    },

    "Kannada": {
        "title": "🩺 ರೋಗಿಯ ಮರುದಾಖಲಾತಿ ಮುನ್ಸೂಚನೆ",
        "button": "🔍 ಮುನ್ಸೂಚನೆ",
        "high": "🔴 30 ದಿನಗಳ ಮರುದಾಖಲಾತಿಯ ಹೆಚ್ಚಿನ ಅಪಾಯ",
        "low": "🟢 30 ದಿನಗಳ ಮರುದಾಖಲಾತಿಯ ಕಡಿಮೆ ಅಪಾಯ",
        "prob": "ಮರುದಾಖಲಾತಿ ಸಾಧ್ಯತೆ",
        "result": "ಮುನ್ಸೂಚನೆ ಫಲಿತಾಂಶ",
        "patient": "ರೋಗಿಯ ID",
        "saved": "ಮುನ್ಸೂಚನೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ.",
    },

    "Hindi": {
        "title": "🩺 रोगी पुनः भर्ती पूर्वानुमान",
        "button": "🔍 पूर्वानुमान करें",
        "high": "🔴 30 दिनों में पुनः भर्ती का उच्च जोखिम",
        "low": "🟢 30 दिनों में पुनः भर्ती का कम जोखिम",
        "prob": "पुनः भर्ती संभावना",
        "result": "पूर्वानुमान परिणाम",
        "patient": "रोगी ID",
        "saved": "पूर्वानुमान सफलतापूर्वक सहेजा गया।",
    },

    "Tamil": {
        "title": "🩺 நோயாளி மீள் சேர்க்கை கணிப்பு",
        "button": "🔍 கணிக்கவும்",
        "high": "🔴 30 நாள் மீள் சேர்க்கைக்கான அதிக ஆபத்து",
        "low": "🟢 30 நாள் மீள் சேர்க்கைக்கான குறைந்த ஆபத்து",
        "prob": "மீள் சேர்க்கை வாய்ப்பு",
        "result": "கணிப்பு முடிவு",
        "patient": "நோயாளி ID",
        "saved": "கணிப்பு வெற்றிகரமாக சேமிக்கப்பட்டது.",
    },

    "Telugu": {
        "title": "🩺 రోగి తిరిగి చేర్పు అంచనా",
        "button": "🔍 అంచనా వేయండి",
        "high": "🔴 30 రోజులలో తిరిగి చేర్పు అధిక ప్రమాదం",
        "low": "🟢 30 రోజులలో తిరిగి చేర్పు తక్కువ ప్రమాదం",
        "prob": "తిరిగి చేర్పు అవకాశం",
        "result": "అంచనా ఫలితం",
        "patient": "రోగి ID",
        "saved": "అంచనా విజయవంతంగా సేవ్ చేయబడింది.",
    },

    "Malayalam": {
        "title": "🩺 രോഗിയുടെ വീണ്ടും പ്രവേശന പ്രവചനം",
        "button": "🔍 പ്രവചിക്കുക",
        "high": "🔴 30 ദിവസത്തെ വീണ്ടും പ്രവേശനത്തിന് ഉയർന്ന അപകടസാധ്യത",
        "low": "🟢 30 ദിവസത്തെ വീണ്ടും പ്രവേശനത്തിന് കുറഞ്ഞ അപകടസാധ്യത",
        "prob": "വീണ്ടും പ്രവേശന സാധ്യത",
        "result": "പ്രവചന ഫലം",
        "patient": "രോഗിയുടെ ID",
        "saved": "പ്രവചനം വിജയകരമായി സംരക്ഷിച്ചു.",
    }
}

T = TEXT.get(lang, TEXT["English"])


# =========================================================
# LOAD PATIENT DATABASE
# =========================================================

@st.cache_data
def load_patients():

    file_path = "patients.csv"

    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:

        df = pd.read_csv(file_path)

        if "patient_id" not in df.columns:
            return pd.DataFrame()

        df["patient_id"] = (
            df["patient_id"]
            .astype(str)
            .str.strip()
        )

        return df

    except Exception:

        return pd.DataFrame()


patients = load_patients()


# =========================================================
# LOAD MODEL
# =========================================================

try:

    model = joblib.load(
        "model/carewatch_lightgbm_model.pkl"
    )

    scaler = joblib.load(
        "model/scaler.pkl"
    )

    encoders = joblib.load(
        "model/label_encoders.pkl"
    )

    feature_columns = joblib.load(
        "model/feature_columns.pkl"
    )

except Exception as e:

    st.error("Unable to load prediction model.")

    st.exception(e)

    st.stop()


# =========================================================
# TITLE
# =========================================================

st.title(T["title"])

st.subheader(
    "AI Powered Hospital Readmission Prediction System"
)

st.markdown("---")


# =========================================================
# PATIENT SELECTION
# =========================================================

st.header("👤 Patient Information")

current_role = st.session_state.get(
    "role",
    "Doctor"
)


# ---------------------------------------------------------
# DOCTOR
# ---------------------------------------------------------

if current_role == "Doctor":

    if patients.empty:

        st.error(
            "patients.csv could not be loaded."
        )

        st.stop()

    patient_ids = sorted(
        patients["patient_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_patient_id = st.selectbox(
        "Select Patient",
        patient_ids
    )

    selected_rows = patients[
        patients["patient_id"]
        == selected_patient_id
    ]

    if selected_rows.empty:

        st.error(
            "Selected patient was not found."
        )

        st.stop()

    patient_record = selected_rows.iloc[0]


# ---------------------------------------------------------
# PATIENT
# ---------------------------------------------------------

else:

    selected_patient_id = st.session_state.get(
        "patient_id"
    )

    if not selected_patient_id:

        st.error(
            "Your Patient ID could not be found in your session."
        )

        st.stop()

    selected_patient_id = str(
        selected_patient_id
    ).strip()

    selected_rows = patients[
        patients["patient_id"]
        == selected_patient_id
    ]

    if selected_rows.empty:

        st.error(
            "Your Patient ID was not found in patients.csv."
        )

        st.stop()

    patient_record = selected_rows.iloc[0]

    st.info(
        f"{T['patient']}: {selected_patient_id}"
    )


# =========================================================
# BASIC PATIENT INFORMATION
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    age_default = patient_record.get(
        "age",
        50
    )

    try:
        age_default = int(float(age_default))
    except:
        age_default = 50

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=age_default
    )


with col2:

    gender_default = str(
        patient_record.get(
            "gender",
            "M"
        )
    )

    gender_options = ["M", "F", "Other"]

    if gender_default not in gender_options:
        gender_default = "Other"

    gender = st.selectbox(
        "Gender",
        gender_options,
        index=gender_options.index(
            gender_default
        )
    )


with col3:

    state_default = str(
        patient_record.get(
            "state",
            ""
        )
    )

    state_classes = list(
        encoders["state"].classes_
    )

    if state_default in state_classes:

        state_index = state_classes.index(
            state_default
        )

    else:

        state_index = 0

    state = st.selectbox(
        "State",
        state_classes,
        index=state_index
    )


# =========================================================
# ADMISSION INFORMATION
# =========================================================

st.markdown("---")

st.header("🏥 Admission Information")

col1, col2 = st.columns(2)


with col1:

    los_days = st.number_input(
        "Length of Stay",
        min_value=1,
        max_value=100,
        value=5
    )

    admit_type = st.selectbox(
        "Admission Type",
        encoders[
            "admit_type"
        ].classes_
    )

    ward_type = st.selectbox(
        "Ward Type",
        encoders[
            "ward_type"
        ].classes_
    )


with col2:

    discharge_type = st.selectbox(
        "Discharge Type",
        encoders[
            "discharge_type"
        ].classes_
    )

    num_procedures = st.number_input(
        "Number of Procedures",
        min_value=0,
        max_value=100,
        value=2
    )

    diagnosis_count = st.number_input(
        "Diagnosis Count",
        min_value=1,
        max_value=50,
        value=3
    )


# =========================================================
# CLINICAL INFORMATION
# =========================================================

st.markdown("---")

st.header("🩸 Clinical Information")

col1, col2 = st.columns(2)


with col1:

    charlson_index = st.number_input(
        "Charlson Index",
        min_value=0,
        max_value=30,
        value=int(
            patient_record.get(
                "comorbidity_count",
                1
            )
        )
    )

    comorbidity_count = st.number_input(
        "Comorbidity Count",
        min_value=0,
        max_value=30,
        value=int(
            patient_record.get(
                "comorbidity_count",
                2
            )
        )
    )

    prev_admissions = st.number_input(
        "Previous Admissions",
        min_value=0,
        max_value=50,
        value=int(
            patient_record.get(
                "prev_admissions",
                0
            )
        )
    )


with col2:

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

    systolic_bp = st.number_input(
        "Systolic BP",
        value=120
    )


# =========================================================
# DIAGNOSIS
# =========================================================

st.markdown("---")

st.header("🧬 Diagnosis")

col1, col2 = st.columns(2)


with col1:

    primary_diagnosis = st.selectbox(
        "Primary Diagnosis",
        encoders[
            "primary_diagnosis"
        ].classes_
    )


with col2:

    primary_category = st.selectbox(
        "Primary Category",
        encoders[
            "primary_category"
        ].classes_
    )


# =========================================================
# HOSPITAL INFORMATION
# =========================================================

st.markdown("---")

st.header("🏥 Hospital Information")

col1, col2 = st.columns(2)


with col1:

    tier = st.selectbox(
        "Hospital Tier",
        encoders[
            "tier"
        ].classes_
    )

    beds = st.number_input(
        "Number of Beds",
        min_value=10,
        max_value=5000,
        value=500
    )


with col2:

    teaching = st.checkbox(
        "Teaching Hospital"
    )


# =========================================================
# FINANCIAL INFORMATION
# =========================================================

st.markdown("---")

st.header("💰 Financial Information")

col1, col2 = st.columns(2)


with col1:

    insurance_type = st.selectbox(
        "Insurance Type",
        encoders[
            "insurance_type"
        ].classes_
    )

    total_cost_inr = st.number_input(
        "Total Cost (INR)",
        min_value=0,
        value=50000
    )

    govt_subsidy_inr = st.number_input(
        "Government Subsidy",
        min_value=0,
        value=10000
    )


with col2:

    out_of_pocket_inr = st.number_input(
        "Out of Pocket Cost",
        min_value=0,
        value=40000
    )

    cost_category = st.selectbox(
        "Cost Category",
        encoders[
            "cost_category"
        ].classes_
    )

    bpl_card = st.checkbox(
        "BPL Card Holder"
    )


# =========================================================
# PREDICT
# =========================================================

st.markdown("---")

predict = st.button(
    T["button"],
    use_container_width=True
)


# =========================================================
# PREDICTION
# =========================================================

if predict:

    try:

        # -------------------------------------------------
        # CREATE DATAFRAME
        # -------------------------------------------------

        patient = pd.DataFrame({

            "los_days": [los_days],

            "admit_type": [admit_type],

            "ward_type": [ward_type],

            "discharge_type": [
                discharge_type
            ],

            "num_procedures": [
                num_procedures
            ],

            "charlson_index": [
                charlson_index
            ],

            "hba1c": [hba1c],

            "creatinine": [
                creatinine
            ],

            "haemoglobin": [
                haemoglobin
            ],

            "systolic_bp": [
                systolic_bp
            ],

            "age": [age],

            "gender": [gender],

            "state": [state],

            "bpl_card": [bpl_card],

            "insurance_type": [
                insurance_type
            ],

            "comorbidity_count": [
                comorbidity_count
            ],

            "prev_admissions": [
                prev_admissions
            ],

            "total_cost_inr": [
                total_cost_inr
            ],

            "govt_subsidy_inr": [
                govt_subsidy_inr
            ],

            "out_of_pocket_inr": [
                out_of_pocket_inr
            ],

            "cost_category": [
                cost_category
            ],

            "tier": [tier],

            "beds": [beds],

            "teaching": [teaching],

            "diagnosis_count": [
                diagnosis_count
            ],

            "primary_diagnosis": [
                primary_diagnosis
            ],

            "primary_category": [
                primary_category
            ]
        })


        # -------------------------------------------------
        # ENCODE
        # -------------------------------------------------

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


        for column in categorical_columns:

            patient[column] = (
                encoders[column]
                .transform(
                    patient[column]
                )
            )


        # -------------------------------------------------
        # BOOLEAN
        # -------------------------------------------------

        patient["bpl_card"] = (
            patient["bpl_card"]
            .astype(int)
        )

        patient["teaching"] = (
            patient["teaching"]
            .astype(int)
        )


        # -------------------------------------------------
        # FEATURE ORDER
        # -------------------------------------------------

        patient = patient[
            feature_columns
        ]


        # -------------------------------------------------
        # SCALE
        # -------------------------------------------------

        patient_scaled = scaler.transform(
            patient
        )


        # -------------------------------------------------
        # PREDICT
        # -------------------------------------------------

        probability = float(
            model.predict_proba(
                patient_scaled
            )[0][1]
        )


        prediction = (
            1
            if probability >= 0.5
            else 0
        )


        # -------------------------------------------------
        # RISK
        # -------------------------------------------------

        if prediction == 1:

            risk_level = "High"

            clinical_summary = (
                "The AI model indicates a higher "
                "risk of 30-day hospital readmission. "
                "Please discuss the result with your "
                "healthcare professional."
            )

            recommendations = [

                "Discuss the assessment with your doctor.",

                "Follow the recommended follow-up schedule.",

                "Continue regular health monitoring."
            ]

        else:

            risk_level = "Low"

            clinical_summary = (
                "The AI model indicates a lower "
                "risk of 30-day hospital readmission."
            )

            recommendations = [

                "Continue following your healthcare plan.",

                "Attend scheduled follow-up appointments.",

                "Maintain regular health monitoring."
            ]


        # =================================================
        # SESSION
        # =================================================

        st.session_state[
            "prediction"
        ] = prediction

        st.session_state[
            "probability"
        ] = probability

        st.session_state[
            "risk_probability"
        ] = probability

        st.session_state[
            "risk_level"
        ] = risk_level

        st.session_state[
            "clinical_summary"
        ] = clinical_summary

        st.session_state[
            "recommendations"
        ] = recommendations


        # =================================================
        # PATIENT INFO SESSION
        # =================================================

        st.session_state[
            "patient_info"
        ] = {

            "Patient ID":
                selected_patient_id,

            "Age":
                age,

            "Gender":
                gender,

            "State":
                state,

            "Admission Type":
                admit_type,

            "Ward":
                ward_type,

            "Discharge Type":
                discharge_type,

            "Primary Diagnosis":
                primary_diagnosis,

            "Disease Category":
                primary_category,

            "Length of Stay":
                los_days,

            "Procedures":
                num_procedures,

            "Charlson Index":
                charlson_index,

            "HbA1c":
                hba1c,

            "Creatinine":
                creatinine,

            "Haemoglobin":
                haemoglobin,

            "Systolic BP":
                systolic_bp,

            "Previous Admissions":
                prev_admissions,

            "Comorbidity Count":
                comorbidity_count
        }


        # =================================================
        # SAVE PREDICTION
        # =================================================

        result_file = (
            "prediction_results.csv"
        )


        new_result = pd.DataFrame([{

            "patient_id":
                selected_patient_id,

            "risk_level":
                risk_level,

            "risk_probability":
                probability,

            "clinical_summary":
                clinical_summary,

            "age":
                age,

            "gender":
                gender,

            "state":
                state,

            "admission_type":
                admit_type,

            "ward_type":
                ward_type,

            "discharge_type":
                discharge_type,

            "primary_diagnosis":
                primary_diagnosis,

            "primary_category":
                primary_category,

            "charlson_index":
                charlson_index,

            "comorbidity_count":
                comorbidity_count,

            "previous_admissions":
                prev_admissions
        }])


        # -------------------------------------------------
        # UPDATE EXISTING DATA
        # -------------------------------------------------

        if os.path.exists(
            result_file
        ):

            old_results = pd.read_csv(
                result_file
            )

            if "patient_id" in old_results.columns:

                old_results[
                    "patient_id"
                ] = (
                    old_results[
                        "patient_id"
                    ]
                    .astype(str)
                    .str.strip()
                )

                # Remove only the selected
                # patient's previous latest record.
                old_results = old_results[
                    old_results[
                        "patient_id"
                    ]
                    != str(
                        selected_patient_id
                    )
                ]

                results = pd.concat(
                    [
                        old_results,
                        new_result
                    ],
                    ignore_index=True
                )

            else:

                results = new_result

        else:

            results = new_result


        results.to_csv(
            result_file,
            index=False
        )


        # =================================================
        # RESULT
        # =================================================

        st.markdown("---")

        st.header(
            T["result"]
        )


        if prediction == 1:

            st.error(
                T["high"]
            )

        else:

            st.success(
                T["low"]
            )


        st.metric(
            T["prob"],
            f"{probability * 100:.2f}%"
        )


        st.info(
            f"{T['patient']}: "
            f"{selected_patient_id}"
        )


        st.success(
            T["saved"]
        )


        # =================================================
        # SUMMARY
        # =================================================

        st.subheader(
            "🧠 Clinical Summary"
        )

        st.info(
            clinical_summary
        )


        # =================================================
        # RECOMMENDATIONS
        # =================================================

        st.subheader(
            "💡 Recommendations"
        )

        for recommendation in recommendations:

            st.success(
                "✅ " + recommendation
            )


    except Exception as e:

        st.error(
            "Prediction Failed"
        )

        st.exception(e)