import os
from datetime import datetime

import joblib
import pandas as pd
import streamlit as st

from auth import require_role
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

require_role("Doctor")


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

PREDICTION_FILE = os.path.join(
    BASE_DIR,
    "prediction_results.csv"
)


# ============================================================
# LOAD FINAL MODEL FILES
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

    threshold = joblib.load(
        os.path.join(
            MODEL_DIR,
            "readmission_threshold.pkl"
        )
    )

    return (
        model,
        feature_columns,
        label_encoders,
        float(threshold)
    )


try:

    (
        model,
        FEATURE_COLUMNS,
        LABEL_ENCODERS,
        FINAL_THRESHOLD
    ) = load_model_files()

except Exception as error:

    st.error(
        "Unable to load the CareWatch-AI prediction model."
    )

    st.exception(error)

    st.stop()


# ============================================================
# VALIDATE FINAL MODEL CONFIGURATION
# ============================================================

if len(FEATURE_COLUMNS) != 27:

    st.error(
        f"Model configuration error: "
        f"expected 27 features but found "
        f"{len(FEATURE_COLUMNS)}."
    )

    st.stop()


# ============================================================
# LOAD DATASETS
# ============================================================

@st.cache_data
def load_csv(filename):

    path = os.path.join(
        BASE_DIR,
        filename
    )

    if not os.path.exists(path):

        return pd.DataFrame()

    try:

        return pd.read_csv(path)

    except Exception:

        return pd.DataFrame()


patients = load_csv(
    "patients.csv"
)

admissions = load_csv(
    "admissions.csv"
)

diagnoses = load_csv(
    "diagnoses.csv"
)

billing = load_csv(
    "billing.csv"
)

hospitals = load_csv(
    "hospitals.csv"
)


# ============================================================
# NORMALIZE IDENTIFIERS
# ============================================================

for dataframe, column in [

    (
        patients,
        "patient_id"
    ),

    (
        admissions,
        "patient_id"
    ),

    (
        admissions,
        "admission_id"
    ),

    (
        diagnoses,
        "admission_id"
    ),

    (
        billing,
        "admission_id"
    ),

    (
        hospitals,
        "hospital_id"
    )

]:

    if (
        not dataframe.empty
        and
        column in dataframe.columns
    ):

        dataframe[column] = (
            dataframe[column]
            .astype(str)
            .str.strip()
        )


# ============================================================
# SAFE VALUE FUNCTIONS
# ============================================================

def safe_float(
    value,
    default=0.0
):

    try:

        number = float(value)

        if pd.isna(number):

            return float(default)

        return number

    except Exception:

        return float(default)


def safe_int(
    value,
    default=0
):

    try:

        number = int(
            float(value)
        )

        return number

    except Exception:

        return int(default)


def safe_bool(value):

    if isinstance(
        value,
        bool
    ):

        return value

    return (
        str(value)
        .strip()
        .lower()
        in [
            "true",
            "1",
            "yes",
            "y",
            "t"
        ]
    )


def safe_text(
    value,
    default="Unknown"
):

    if value is None:

        return default

    try:

        if pd.isna(value):

            return default

    except Exception:

        pass

    text = str(
        value
    ).strip()

    if (
        not text
        or
        text.lower()
        in [
            "nan",
            "none",
            "null"
        ]
    ):

        return default

    return text


# ============================================================
# HEADER
# ============================================================

st.title(
    "🧠 Patient Readmission Prediction"
)

st.caption(
    "AI-Based Hospital Readmission Prediction "
    "and Clinical Decision Support"
)

st.markdown("---")


# ============================================================
# DATA VALIDATION
# ============================================================

if patients.empty:

    st.error(
        "patients.csv could not be loaded."
    )

    st.stop()


if admissions.empty:

    st.error(
        "admissions.csv could not be loaded. "
        "Admission-level information is required "
        "for the final 27-feature model."
    )

    st.stop()


# ============================================================
# PATIENT SELECTION
# ============================================================

st.header(
    "👤 Patient Selection"
)

patient_ids = (
    patients[
        "patient_id"
    ]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)

patient_ids = sorted(
    patient_ids
)

if not patient_ids:

    st.error(
        "No patients are available."
    )

    st.stop()


selected_patient_id = st.selectbox(
    "Select Patient",
    patient_ids
)

patient_id = str(
    selected_patient_id
).strip()


# ============================================================
# PATIENT RECORD
# ============================================================

patient_rows = patients[
    patients[
        "patient_id"
    ] == patient_id
]


if patient_rows.empty:

    st.error(
        "Selected patient was not found."
    )

    st.stop()


patient = patient_rows.iloc[0]


# ============================================================
# PATIENT ADMISSIONS
# ============================================================

patient_admissions = admissions[
    admissions[
        "patient_id"
    ] == patient_id
].copy()


if patient_admissions.empty:

    st.error(
        "No admission record was found for this patient. "
        "The final model requires admission-level features."
    )

    st.stop()


# ============================================================
# SORT ADMISSIONS AND SELECT LATEST ADMISSION
# ============================================================

if (
    "admit_date"
    in patient_admissions.columns
):

    patient_admissions[
        "_parsed_admit_date"
    ] = pd.to_datetime(
        patient_admissions[
            "admit_date"
        ],
        errors="coerce"
    )

    patient_admissions = (
        patient_admissions
        .sort_values(
            "_parsed_admit_date",
            ascending=False
        )
    )


latest_admission = (
    patient_admissions
    .iloc[0]
)

latest_admission_id = safe_text(
    latest_admission.get(
        "admission_id"
    ),
    ""
)


if not latest_admission_id:

    st.error(
        "Latest admission ID is unavailable."
    )

    st.stop()


# ============================================================
# EHR DISPLAY
# ============================================================

st.markdown("---")

st.header(
    "🏥 Electronic Health Record"
)

st.caption(
    "Patient information is automatically retrieved "
    "from the CareWatch-AI EHR datasets."
)


# ============================================================
# PATIENT INFORMATION
# ============================================================

st.subheader(
    "👤 Patient Information"
)

c1, c2, c3, c4, c5 = st.columns(
    5
)

with c1:

    st.metric(
        "Patient ID",
        patient_id
    )

with c2:

    st.metric(
        "Age",
        safe_text(
            patient.get(
                "age"
            )
        )
    )

with c3:

    st.metric(
        "Gender",
        safe_text(
            patient.get(
                "gender"
            )
        )
    )

with c4:

    st.metric(
        "State",
        safe_text(
            patient.get(
                "state"
            )
        )
    )

with c5:

    st.metric(
        "Comorbidities",
        safe_text(
            patient.get(
                "comorbidity_count"
            )
        )
    )


c1, c2, c3 = st.columns(
    3
)

with c1:

    st.info(
        f"**BPL Card:** "
        f"{safe_text(patient.get('bpl_card'))}"
    )

with c2:

    st.info(
        f"**Insurance:** "
        f"{safe_text(patient.get('insurance_type'))}"
    )

with c3:

    st.info(
        f"**Previous Admissions:** "
        f"{safe_text(patient.get('prev_admissions'))}"
    )


# ============================================================
# LATEST ADMISSION INFORMATION
# ============================================================

st.subheader(
    "🏥 Latest Admission"
)

st.write(
    f"**Admission ID:** "
    f"{latest_admission_id}"
)

c1, c2, c3, c4 = st.columns(
    4
)

with c1:

    st.metric(
        "Admission Type",
        safe_text(
            latest_admission.get(
                "admit_type"
            )
        )
    )

with c2:

    st.metric(
        "Ward Type",
        safe_text(
            latest_admission.get(
                "ward_type"
            )
        )
    )

with c3:

    st.metric(
        "Discharge Type",
        safe_text(
            latest_admission.get(
                "discharge_type"
            )
        )
    )

with c4:

    st.metric(
        "Length of Stay",
        safe_text(
            latest_admission.get(
                "los_days"
            )
        )
    )


# ============================================================
# DIAGNOSIS INFORMATION
# ============================================================
# IMPORTANT:
# Training aggregated diagnosis information per admission.
# Therefore prediction must use diagnosis information from
# the selected latest admission only.
# ============================================================

latest_diagnoses = pd.DataFrame()

if (
    not diagnoses.empty
    and
    "admission_id"
    in diagnoses.columns
):

    latest_diagnoses = diagnoses[
        diagnoses[
            "admission_id"
        ].astype(str)
        ==
        latest_admission_id
    ].copy()


diagnosis_count = 0

primary_diagnosis = "Unknown"

primary_category = "Unknown"


if not latest_diagnoses.empty:

    diagnosis_count = len(
        latest_diagnoses
    )

    if (
        "diag_rank"
        in latest_diagnoses.columns
    ):

        ranked = (
            latest_diagnoses
            .copy()
        )

        ranked[
            "_rank"
        ] = pd.to_numeric(
            ranked[
                "diag_rank"
            ],
            errors="coerce"
        )

        ranked = (
            ranked
            .sort_values(
                "_rank",
                ascending=True
            )
        )

        primary_row = (
            ranked.iloc[0]
        )

    else:

        primary_row = (
            latest_diagnoses
            .iloc[0]
        )


    # --------------------------------------------------------
    # IMPORTANT:
    # Notebook training used diag_desc as primary_diagnosis,
    # NOT icd10_code.
    # --------------------------------------------------------

    primary_diagnosis = safe_text(
        primary_row.get(
            "diag_desc"
        ),
        "Unknown"
    )

    primary_category = safe_text(
        primary_row.get(
            "diag_category"
        ),
        "Unknown"
    )

else:

    st.info(
        "No diagnosis records were found "
        "for the latest admission."
    )


# ============================================================
# HOSPITAL INFORMATION
# ============================================================

hospital_tier = "Unknown"

hospital_beds = 0

hospital_teaching = False


hospital_id = safe_text(
    latest_admission.get(
        "hospital_id"
    ),
    ""
)


if (
    hospital_id
    and
    not hospitals.empty
    and
    "hospital_id"
    in hospitals.columns
):

    hospital_rows = hospitals[
        hospitals[
            "hospital_id"
        ].astype(str)
        ==
        hospital_id
    ]


    if not hospital_rows.empty:

        hospital = (
            hospital_rows
            .iloc[0]
        )

        hospital_tier = safe_text(
            hospital.get(
                "tier"
            ),
            "Unknown"
        )

        hospital_beds = safe_int(
            hospital.get(
                "beds"
            ),
            0
        )

        hospital_teaching = safe_bool(
            hospital.get(
                "teaching"
            )
        )


# ============================================================
# BILLING INFORMATION
# ============================================================
# IMPORTANT:
# Billing is also admission-level in the training dataset.
# Use the latest admission only.
# ============================================================

total_cost = 0.0

govt_subsidy = 0.0

out_of_pocket = 0.0

cost_category = "Unknown"


latest_billing = pd.DataFrame()


if (
    not billing.empty
    and
    "admission_id"
    in billing.columns
):

    latest_billing = billing[
        billing[
            "admission_id"
        ].astype(str)
        ==
        latest_admission_id
    ].copy()


if not latest_billing.empty:

    billing_row = (
        latest_billing
        .iloc[0]
    )

    total_cost = safe_float(
        billing_row.get(
            "total_cost_inr"
        ),
        0
    )

    govt_subsidy = safe_float(
        billing_row.get(
            "govt_subsidy_inr"
        ),
        0
    )

    out_of_pocket = safe_float(
        billing_row.get(
            "out_of_pocket_inr"
        ),
        0
    )

    cost_category = safe_text(
        billing_row.get(
            "cost_category"
        ),
        "Unknown"
    )


# ============================================================
# DEFAULT PATIENT VALUES
# ============================================================

default_age = safe_int(
    patient.get(
        "age"
    ),
    50
)

default_gender = safe_text(
    patient.get(
        "gender"
    ),
    "Unknown"
)

default_state = safe_text(
    patient.get(
        "state"
    ),
    "Unknown"
)

default_bpl = safe_bool(
    patient.get(
        "bpl_card"
    )
)

default_insurance = safe_text(
    patient.get(
        "insurance_type"
    ),
    "Unknown"
)

default_comorbidity = safe_int(
    patient.get(
        "comorbidity_count"
    ),
    0
)

default_previous = safe_int(
    patient.get(
        "prev_admissions"
    ),
    0
)


# ============================================================
# DEFAULT ADMISSION VALUES
# ============================================================

default_los = safe_int(
    latest_admission.get(
        "los_days"
    ),
    1
)

default_admit_type = safe_text(
    latest_admission.get(
        "admit_type"
    ),
    "Unknown"
)

default_ward_type = safe_text(
    latest_admission.get(
        "ward_type"
    ),
    "Unknown"
)

default_discharge_type = safe_text(
    latest_admission.get(
        "discharge_type"
    ),
    "Unknown"
)

default_procedures = safe_int(
    latest_admission.get(
        "num_procedures"
    ),
    0
)

default_charlson = safe_float(
    latest_admission.get(
        "charlson_index"
    ),
    0
)

default_hba1c = safe_float(
    latest_admission.get(
        "hba1c"
    ),
    0
)

default_creatinine = safe_float(
    latest_admission.get(
        "creatinine"
    ),
    0
)

default_haemoglobin = safe_float(
    latest_admission.get(
        "haemoglobin"
    ),
    0
)

default_sbp = safe_float(
    latest_admission.get(
        "systolic_bp"
    ),
    120
)


# ============================================================
# AI PREDICTION INPUTS
# ============================================================

st.markdown("---")

st.header(
    "🤖 AI Readmission Risk Prediction"
)

st.caption(
    "Values are pre-filled from the patient's EHR. "
    "The doctor may review them before running "
    "the prediction."
)


# ============================================================
# DEMOGRAPHIC AND ADMISSION INPUTS
# ============================================================

c1, c2, c3 = st.columns(
    3
)

with c1:

    age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=int(
            default_age
        ),
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


c1, c2, c3 = st.columns(
    3
)

with c1:

    los_days = st.number_input(
        "Length of Stay",
        min_value=0,
        max_value=365,
        value=int(
            default_los
        ),
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


c1, c2, c3 = st.columns(
    3
)

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
        value=int(
            default_procedures
        ),
        step=1
    )

with c3:

    charlson_index = st.number_input(
        "Charlson Index",
        min_value=0.0,
        max_value=50.0,
        value=float(
            default_charlson
        ),
        step=0.1
    )


c1, c2, c3 = st.columns(
    3
)

with c1:

    prev_admissions = st.number_input(
        "Previous Admissions",
        min_value=0,
        max_value=100,
        value=int(
            default_previous
        ),
        step=1
    )

with c2:

    comorbidity_count = st.number_input(
        "Comorbidity Count",
        min_value=0,
        max_value=50,
        value=int(
            default_comorbidity
        ),
        step=1
    )

with c3:

    diagnosis_count_input = st.number_input(
        "Diagnosis Count",
        min_value=0,
        max_value=100,
        value=int(
            diagnosis_count
        ),
        step=1
    )


# ============================================================
# CLINICAL INFORMATION
# ============================================================

st.subheader(
    "🩸 Clinical Information"
)

c1, c2, c3, c4 = st.columns(
    4
)

with c1:

    hba1c = st.number_input(
        "HbA1c",
        min_value=0.0,
        max_value=30.0,
        value=float(
            default_hba1c
        ),
        step=0.1
    )

with c2:

    creatinine = st.number_input(
        "Creatinine",
        min_value=0.0,
        max_value=30.0,
        value=float(
            default_creatinine
        ),
        step=0.1
    )

with c3:

    haemoglobin = st.number_input(
        "Haemoglobin",
        min_value=0.0,
        max_value=30.0,
        value=float(
            default_haemoglobin
        ),
        step=0.1
    )

with c4:

    systolic_bp = st.number_input(
        "Systolic BP",
        min_value=0.0,
        max_value=300.0,
        value=float(
            default_sbp
        ),
        step=1.0
    )


c1, c2, c3 = st.columns(
    3
)

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
        int(
            diagnosis_count_input
        )
    )


# ============================================================
# HOSPITAL INFORMATION
# ============================================================

st.subheader(
    "🏥 Hospital Information"
)

c1, c2, c3 = st.columns(
    3
)

with c1:

    hospital_tier_input = st.text_input(
        "Hospital Tier",
        value=str(
            hospital_tier
        )
    )

with c2:

    hospital_beds_input = st.number_input(
        "Number of Beds",
        min_value=0,
        max_value=10000,
        value=int(
            hospital_beds
        ),
        step=1
    )

with c3:

    teaching_input = st.checkbox(
        "Teaching Hospital",
        value=bool(
            hospital_teaching
        )
    )


# ============================================================
# FINANCIAL INFORMATION
# ============================================================

st.subheader(
    "💰 Financial Information"
)

insurance_type = st.text_input(
    "Insurance Type",
    value=default_insurance
)


c1, c2, c3 = st.columns(
    3
)

with c1:

    total_cost_inr = st.number_input(
        "Total Cost (INR)",
        min_value=0.0,
        max_value=100000000.0,
        value=float(
            total_cost
        ),
        step=100.0
    )

with c2:

    govt_subsidy_inr = st.number_input(
        "Government Subsidy (INR)",
        min_value=0.0,
        max_value=100000000.0,
        value=float(
            govt_subsidy
        ),
        step=100.0
    )

with c3:

    out_of_pocket_inr = st.number_input(
        "Out-of-Pocket Cost (INR)",
        min_value=0.0,
        max_value=100000000.0,
        value=float(
            out_of_pocket
        ),
        step=100.0
    )


cost_category_input = st.text_input(
    "Cost Category",
    value=str(
        cost_category
    )
)

bpl_card_input = st.checkbox(
    "BPL Card Holder",
    value=bool(
        default_bpl
    )
)


# ============================================================
# RAW 27-FEATURE INPUT
# ============================================================

raw_features = {

    "los_days":
        float(
            los_days
        ),

    "admit_type":
        safe_text(
            admit_type
        ),

    "ward_type":
        safe_text(
            ward_type
        ),

    "discharge_type":
        safe_text(
            discharge_type
        ),

    "num_procedures":
        float(
            num_procedures
        ),

    "charlson_index":
        float(
            charlson_index
        ),

    "hba1c":
        float(
            hba1c
        ),

    "creatinine":
        float(
            creatinine
        ),

    "haemoglobin":
        float(
            haemoglobin
        ),

    "systolic_bp":
        float(
            systolic_bp
        ),

    "age":
        float(
            age
        ),

    "gender":
        safe_text(
            gender
        ),

    "state":
        safe_text(
            state
        ),

    "bpl_card":
        bool(
            bpl_card_input
        ),

    "insurance_type":
        safe_text(
            insurance_type
        ),

    "comorbidity_count":
        float(
            comorbidity_count
        ),

    "prev_admissions":
        float(
            prev_admissions
        ),

    "total_cost_inr":
        float(
            total_cost_inr
        ),

    "govt_subsidy_inr":
        float(
            govt_subsidy_inr
        ),

    "out_of_pocket_inr":
        float(
            out_of_pocket_inr
        ),

    "cost_category":
        safe_text(
            cost_category_input
        ),

    "tier":
        safe_text(
            hospital_tier_input
        ),

    "beds":
        float(
            hospital_beds_input
        ),

    "teaching":
        bool(
            teaching_input
        ),

    "diagnosis_count":
        float(
            diagnosis_count_input
        ),

    "primary_diagnosis":
        safe_text(
            primary_diagnosis_input
        ),

    "primary_category":
        safe_text(
            primary_category_input
        )
}


# ============================================================
# CATEGORICAL ENCODING
# ============================================================

def encode_value(
    column,
    value
):

    if (
        column
        not in LABEL_ENCODERS
    ):

        return value


    encoder = (
        LABEL_ENCODERS[
            column
        ]
    )


    value_string = safe_text(
        value
    )


    classes = [
        str(item)
        for item
        in getattr(
            encoder,
            "classes_",
            []
        )
    ]


    if (
        value_string
        in classes
    ):

        return int(
            encoder.transform(
                [
                    value_string
                ]
            )[0]
        )


    # --------------------------------------------------------
    # Prefer explicit Unknown category when available.
    # --------------------------------------------------------

    if (
        "Unknown"
        in classes
    ):

        return int(
            encoder.transform(
                [
                    "Unknown"
                ]
            )[0]
        )


    # --------------------------------------------------------
    # Otherwise use first known training category.
    # --------------------------------------------------------

    if classes:

        fallback = (
            classes[0]
        )

        return int(
            encoder.transform(
                [
                    fallback
                ]
            )[0]
        )


    return 0


# ============================================================
# PREPARE FINAL MODEL INPUT
# ============================================================

def prepare_model_input():

    dataframe = pd.DataFrame(
        [
            raw_features
        ]
    )


    # --------------------------------------------------------
    # Ensure all expected model features exist
    # --------------------------------------------------------

    for feature in FEATURE_COLUMNS:

        if (
            feature
            not in dataframe.columns
        ):

            dataframe[
                feature
            ] = 0


    # --------------------------------------------------------
    # Exact training feature order
    # --------------------------------------------------------

    dataframe = dataframe[
        FEATURE_COLUMNS
    ].copy()


    # --------------------------------------------------------
    # Encode saved categorical columns
    # --------------------------------------------------------

    for column in LABEL_ENCODERS.keys():

        if (
            column
            in dataframe.columns
        ):

            dataframe[
                column
            ] = dataframe[
                column
            ].apply(
                lambda value:
                encode_value(
                    column,
                    value
                )
            )


    # --------------------------------------------------------
    # Boolean conversion if boolean columns were not encoded
    # --------------------------------------------------------

    for column in [
        "bpl_card",
        "teaching"
    ]:

        if (
            column
            in dataframe.columns
            and
            column
            not in LABEL_ENCODERS
        ):

            dataframe[
                column
            ] = dataframe[
                column
            ].astype(int)


    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    for column in dataframe.columns:

        dataframe[
            column
        ] = pd.to_numeric(
            dataframe[
                column
            ],
            errors="coerce"
        )


    dataframe = dataframe.fillna(
        0
    )


    return dataframe


# ============================================================
# SHOW FINAL MODEL CONFIGURATION
# ============================================================

with st.expander(
    "ℹ️ Prediction Model Information"
):

    st.write(
        "**Model:** Class-Weighted LightGBM"
    )

    st.write(
        f"**Number of Features:** "
        f"{len(FEATURE_COLUMNS)}"
    )

    st.write(
        f"**Binary Readmission Threshold:** "
        f"{FINAL_THRESHOLD:.2f}"
    )

    st.caption(
        "The 0.55 threshold determines the binary "
        "30-day readmission prediction. "
        "Low, Moderate and High categories are "
        "separate application-level risk bands."
    )


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
# RUN FINAL LIGHTGBM PREDICTION
# ============================================================

if predict_clicked:

    try:

        model_input = (
            prepare_model_input()
        )


        # ====================================================
        # IMPORTANT:
        # DO NOT APPLY StandardScaler HERE.
        #
        # The final Class-Weighted LightGBM was trained on
        # the original encoded, unscaled feature matrix.
        # ====================================================

        probabilities = (
            model.predict_proba(
                model_input
            )
        )

        probability = float(
            probabilities[
                0
            ][
                1
            ]
        )


        probability = max(
            0.0,
            min(
                1.0,
                probability
            )
        )


        percentage = (
            probability
            *
            100.0
        )


        # ====================================================
        # FINAL BINARY READMISSION DECISION
        # ====================================================

        predicted_readmission = int(
            probability
            >=
            FINAL_THRESHOLD
        )


        readmission_label = (
            "Yes"
            if predicted_readmission == 1
            else "No"
        )


        # ====================================================
        # APPLICATION RISK BANDS
        # ====================================================
        # These are display categories and are separate from
        # the final 0.55 binary model threshold.
        # ====================================================

        if probability >= 0.60:

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


        elif probability >= 0.30:

            risk_level = "Moderate"

            risk_icon = "🟠"

            clinical_summary = (
                "The AI model indicates a moderate risk "
                "of 30-day hospital readmission. "
                "Additional clinical monitoring "
                "may be appropriate."
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
        # SAVE PREDICTION
        # ====================================================

        prediction_timestamp = (
            datetime.now()
            .isoformat()
        )


        prediction_record = {

            "timestamp":
                prediction_timestamp,

            "patient_id":
                patient_id,

            "admission_id":
                latest_admission_id,

            "predicted_readmission":
                predicted_readmission,

            "readmission_label":
                readmission_label,

            # Main probability column used by dashboard
            "risk_probability":
                round(
                    percentage,
                    4
                ),

            # Retained for compatibility with older pages
            "readmission_probability":
                round(
                    percentage,
                    4
                ),

            "binary_threshold":
                round(
                    FINAL_THRESHOLD,
                    4
                ),

            "risk_level":
                risk_level,

            "clinical_summary":
                clinical_summary

        }


        new_prediction = pd.DataFrame(
            [
                prediction_record
            ]
        )


        if os.path.exists(
            PREDICTION_FILE
        ):

            try:

                existing_predictions = (
                    pd.read_csv(
                        PREDICTION_FILE
                    )
                )


                prediction_df = pd.concat(
                    [
                        existing_predictions,
                        new_prediction
                    ],
                    ignore_index=True
                )

            except Exception:

                prediction_df = (
                    new_prediction
                )

        else:

            prediction_df = (
                new_prediction
            )


        prediction_df.to_csv(
            PREDICTION_FILE,
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


        st.session_state[
            "last_model_input"
        ] = model_input


        # ====================================================
        # BLOCKCHAIN RECORD
        # ====================================================

        blockchain_success = False

        blockchain_message = ""


        try:

            blockchain_record = {

                "patient_id":
                    patient_id,

                "admission_id":
                    latest_admission_id,

                "predicted_readmission":
                    predicted_readmission,

                "readmission_probability":
                    round(
                        percentage,
                        4
                    ),

                "binary_threshold":
                    round(
                        FINAL_THRESHOLD,
                        4
                    ),

                "risk_level":
                    risk_level,

                "clinical_summary":
                    clinical_summary,

                "recommendations":
                    recommendations,

                "timestamp":
                    prediction_timestamp,

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


            block_index = (
                block.get(
                    "block_index",
                    block.get(
                        "index",
                        "N/A"
                    )
                )
                if isinstance(
                    block,
                    dict
                )
                else "N/A"
            )


            blockchain_message = (
                f"Blockchain block "
                f"{block_index} "
                f"created successfully."
            )


        except Exception as blockchain_error:

            blockchain_message = str(
                blockchain_error
            )


        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        st.markdown("---")

        st.header(
            "📊 Prediction Result"
        )


        st.success(
            "Prediction saved successfully."
        )


        c1, c2, c3, c4 = st.columns(
            4
        )


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
                "30-Day Readmission",
                readmission_label
            )


        with c4:

            st.metric(
                "Model Threshold",
                f"{FINAL_THRESHOLD:.2f}"
            )


        st.markdown(
            f"# {risk_icon} "
            f"{risk_level} Risk"
        )


        st.caption(
            f"Patient ID: {patient_id}"
        )


        # ====================================================
        # BINARY MODEL INTERPRETATION
        # ====================================================

        if predicted_readmission == 1:

            st.warning(
                "The final Class-Weighted LightGBM "
                "model classifies this patient as "
                "predicted for 30-day readmission "
                f"at the {FINAL_THRESHOLD:.2f} "
                "operating threshold."
            )

        else:

            st.info(
                "The final Class-Weighted LightGBM "
                "model does not classify this patient "
                "as predicted for 30-day readmission "
                f"at the {FINAL_THRESHOLD:.2f} "
                "operating threshold."
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

                verification = (
                    verify_blockchain()
                )


                if isinstance(
                    verification,
                    tuple
                ):

                    valid, message = (
                        verification
                    )

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
                    "but verification could not "
                    "be completed."
                )

                st.caption(
                    str(
                        verification_error
                    )
                )


        else:

            st.warning(
                "Prediction was saved, but the "
                "blockchain audit record could "
                "not be created."
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


        c1, c2, c3 = st.columns(
            3
        )


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