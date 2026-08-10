import streamlit as st
import os
import pandas as pd


# =========================================================
# SESSION INITIALIZATION
# =========================================================

def initialize_session():

    defaults = {
        "authenticated": False,
        "username": None,
        "role": None,

        # Patient identity
        "patient_id": None,
        "patient_name": None,
        "patient_age": None,
        "patient_gender": None,
        "patient_hospital": None,
        "patient_doctor": None,
        "patient_state": None,

        # Prediction information
        "prediction": None,
        "probability": None,
        "risk_probability": None,
        "risk_level": None,
        "clinical_summary": "",
        "recommendations": [],

        # Reports
        "report": None,

        # Language
        "language": "English",
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# =========================================================
# ADMIN / DOCTOR USERS
# =========================================================

USERS = {

    "admin": {
        "password": "admin123",
        "role": "Admin",
    },

    "doctor": {
        "password": "doctor123",
        "role": "Doctor",
    },
}


# =========================================================
# LOAD PATIENT DATA
# =========================================================

@st.cache_data
def load_patients():

    patient_file = "patients.csv"

    if not os.path.exists(patient_file):
        return pd.DataFrame()

    try:

        df = pd.read_csv(patient_file)

        if df.empty:
            return pd.DataFrame()

        # Find patient ID column
        possible_id_columns = [
            "patient_id",
            "patientId",
            "Patient_ID",
            "id",
            "ID",
        ]

        id_column = None

        for column in possible_id_columns:

            if column in df.columns:
                id_column = column
                break

        if id_column is None:
            return pd.DataFrame()

        # Standardize column name
        if id_column != "patient_id":

            df = df.rename(
                columns={
                    id_column: "patient_id"
                }
            )

        # Clean patient IDs
        df["patient_id"] = (
            df["patient_id"]
            .astype(str)
            .str.strip()
        )

        # Remove invalid IDs
        df = df[
            (df["patient_id"] != "")
            &
            (df["patient_id"].str.lower() != "nan")
        ]

        return df

    except Exception:

        return pd.DataFrame()
# =========================================================
# LOAD PREDICTION DATA
# =========================================================

@st.cache_data
def load_prediction_data():

    result_file = "prediction_results.csv"

    if not os.path.exists(result_file):
        return pd.DataFrame()

    try:

        df = pd.read_csv(result_file)

        if df.empty:
            return pd.DataFrame()

        if "patient_id" in df.columns:

            df["patient_id"] = (
                df["patient_id"]
                .astype(str)
                .str.strip()
            )

        return df

    except Exception:

        return pd.DataFrame()

# =========================================================
# GET ONE PATIENT
# =========================================================

def get_patient(patient_id):

    patients = load_patients()

    if patients.empty:
        return None

    patient_id = str(patient_id).strip()

    rows = patients[
        patients["patient_id"].astype(str).str.strip()
        == patient_id
    ]

    if rows.empty:
        return None

    return rows.iloc[0]


# =========================================================
# HELPER: SAFE VALUE
# =========================================================

def safe_value(patient, column, default="N/A"):

    if column not in patient.index:
        return default

    value = patient[column]

    if pd.isna(value):
        return default

    return value


# =========================================================
# PATIENT LOGIN
# =========================================================

def authenticate_patient(username, password):

    """
    Dynamic patient authentication.

    Username:
        Patient ID from patients.csv

    Password:
        patient123

    Example:

        Username: <patient_id_from_csv>
        Password: patient123

    Every patient contained in patients.csv can log in.
    """

    patient_id = str(username).strip()

    if not patient_id:
        return False

    # -----------------------------------------------------
    # Patient demo password
    # -----------------------------------------------------

    if password != "patient123":
        return False

    # -----------------------------------------------------
    # Find patient in patients.csv
    # -----------------------------------------------------

    patient = get_patient(patient_id)

    if patient is None:
        return False

    # -----------------------------------------------------
    # AUTHENTICATION
    # -----------------------------------------------------

    st.session_state["authenticated"] = True
    st.session_state["username"] = patient_id
    st.session_state["role"] = "Patient"

    # -----------------------------------------------------
    # PATIENT ID
    # -----------------------------------------------------

    st.session_state["patient_id"] = patient_id

    # -----------------------------------------------------
    # BASIC INFORMATION
    # -----------------------------------------------------

    st.session_state["patient_name"] = safe_value(
        patient,
        "name",
        patient_id
    )

    st.session_state["patient_age"] = safe_value(
        patient,
        "age",
        "N/A"
    )

    st.session_state["patient_gender"] = safe_value(
        patient,
        "gender",
        "N/A"
    )

    st.session_state["patient_state"] = safe_value(
        patient,
        "state",
        "N/A"
    )

    st.session_state["patient_hospital"] = safe_value(
        patient,
        "hospital",
        "CareWatch General Hospital"
    )

    st.session_state["patient_doctor"] = safe_value(
        patient,
        "doctor",
        "Dr. Assigned"
    )

    # -----------------------------------------------------
    # CLEAR OLD PREDICTION SESSION DATA
    # -----------------------------------------------------

    st.session_state["prediction"] = None
    st.session_state["probability"] = None
    st.session_state["risk_probability"] = None
    st.session_state["risk_level"] = None

    st.session_state["clinical_summary"] = ""
    st.session_state["recommendations"] = []

    st.session_state["report"] = None

    return True


# =========================================================
# MAIN LOGIN
# =========================================================

def login(username, password):

    initialize_session()

    username = str(username).strip()

    if not username or not password:
        return False

    # =====================================================
    # ADMIN / DOCTOR LOGIN
    # =====================================================

    username_lower = username.lower()

    if username_lower in USERS:

        user = USERS[username_lower]

        if user["password"] == password:

            # Authentication
            st.session_state["authenticated"] = True

            st.session_state["username"] = username_lower

            st.session_state["role"] = user["role"]

            # -------------------------------------------------
            # Clear patient-specific information
            # -------------------------------------------------

            st.session_state["patient_id"] = None
            st.session_state["patient_name"] = None
            st.session_state["patient_age"] = None
            st.session_state["patient_gender"] = None
            st.session_state["patient_hospital"] = None
            st.session_state["patient_doctor"] = None
            st.session_state["patient_state"] = None

            st.session_state["prediction"] = None
            st.session_state["probability"] = None
            st.session_state["risk_probability"] = None
            st.session_state["risk_level"] = None

            st.session_state["clinical_summary"] = ""
            st.session_state["recommendations"] = []

            st.session_state["report"] = None

            return True

    # =====================================================
    # PATIENT LOGIN
    # =====================================================

    return authenticate_patient(
        username,
        password
    )


# =========================================================
# LOGOUT
# =========================================================

def logout():

    # Authentication
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None

    # Patient information
    st.session_state["patient_id"] = None
    st.session_state["patient_name"] = None
    st.session_state["patient_age"] = None
    st.session_state["patient_gender"] = None
    st.session_state["patient_hospital"] = None
    st.session_state["patient_doctor"] = None
    st.session_state["patient_state"] = None

    # Prediction
    st.session_state["prediction"] = None
    st.session_state["probability"] = None
    st.session_state["risk_probability"] = None
    st.session_state["risk_level"] = None

    st.session_state["clinical_summary"] = ""
    st.session_state["recommendations"] = []

    # Reports
    st.session_state["report"] = None

    st.rerun()


# =========================================================
# REQUIRE LOGIN
# =========================================================

def require_login():

    initialize_session()

    if not st.session_state["authenticated"]:

        st.warning(
            "Please login to access this page."
        )

        st.stop()


# =========================================================
# REQUIRE ROLE
# =========================================================

def require_role(allowed_roles):

    require_login()

    current_role = st.session_state.get(
        "role"
    )

    if current_role not in allowed_roles:

        st.error(
            "You are not authorized to access this page."
        )

        st.stop()