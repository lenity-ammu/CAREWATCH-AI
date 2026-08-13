import os
import json
import pandas as pd


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# =========================================================
# DATA FILES
# =========================================================

PATIENT_FILE = os.path.join(
    BASE_DIR,
    "patients.csv"
)

ADMISSION_FILE = os.path.join(
    BASE_DIR,
    "admissions.csv"
)

DIAGNOSIS_FILE = os.path.join(
    BASE_DIR,
    "diagnoses.csv"
)

BILLING_FILE = os.path.join(
    BASE_DIR,
    "billing.csv"
)

HOSPITAL_FILE = os.path.join(
    BASE_DIR,
    "hospitals.csv"
)

PREDICTION_FILE = os.path.join(
    BASE_DIR,
    "prediction_results.csv"
)

REPORT_FILE = os.path.join(
    BASE_DIR,
    "patient_reports.json"
)


# =========================================================
# GENERIC CSV LOADER
# =========================================================

def load_csv(file_path):

    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:

        return pd.read_csv(file_path)

    except Exception:

        return pd.DataFrame()


# =========================================================
# PATIENTS
# =========================================================

def load_patients():

    df = load_csv(PATIENT_FILE)

    if df.empty:
        return df

    if "patient_id" in df.columns:

        df["patient_id"] = (
            df["patient_id"]
            .astype(str)
            .str.strip()
        )

    return df


# =========================================================
# GET SINGLE PATIENT
# =========================================================

def get_patient(patient_id):

    patients = load_patients()

    if patients.empty:
        return None

    patient_id = str(
        patient_id
    ).strip()

    rows = patients[
        patients["patient_id"]
        .astype(str)
        .str.strip()
        == patient_id
    ]

    if rows.empty:
        return None

    return rows.iloc[0]


# =========================================================
# ADMISSIONS
# =========================================================

def get_admissions(patient_id):

    admissions = load_csv(
        ADMISSION_FILE
    )

    if admissions.empty:
        return admissions

    if "patient_id" not in admissions.columns:
        return pd.DataFrame()

    patient_id = str(
        patient_id
    ).strip()

    result = admissions[
        admissions["patient_id"]
        .astype(str)
        .str.strip()
        == patient_id
    ].copy()

    return result


# =========================================================
# DIAGNOSES
# =========================================================

def get_diagnoses(patient_id):

    diagnoses = load_csv(
        DIAGNOSIS_FILE
    )

    if diagnoses.empty:
        return diagnoses

    if "admission_id" not in diagnoses.columns:
        return pd.DataFrame()

    admissions = get_admissions(
        patient_id
    )

    if admissions.empty:
        return pd.DataFrame()

    admission_ids = (
        admissions["admission_id"]
        .astype(str)
        .str.strip()
        .tolist()
    )

    diagnoses["admission_id"] = (
        diagnoses["admission_id"]
        .astype(str)
        .str.strip()
    )

    result = diagnoses[
        diagnoses["admission_id"]
        .isin(admission_ids)
    ].copy()

    return result


# =========================================================
# BILLING
# =========================================================

def get_billing(patient_id):

    billing = load_csv(
        BILLING_FILE
    )

    if billing.empty:
        return billing

    if "admission_id" not in billing.columns:
        return pd.DataFrame()

    admissions = get_admissions(
        patient_id
    )

    if admissions.empty:
        return pd.DataFrame()

    admission_ids = (
        admissions["admission_id"]
        .astype(str)
        .str.strip()
        .tolist()
    )

    billing["admission_id"] = (
        billing["admission_id"]
        .astype(str)
        .str.strip()
    )

    result = billing[
        billing["admission_id"]
        .isin(admission_ids)
    ].copy()

    return result


# =========================================================
# HOSPITAL INFORMATION
# =========================================================

def get_hospitals():

    return load_csv(
        HOSPITAL_FILE
    )


def get_hospital_for_admission(
    hospital_id
):

    hospitals = get_hospitals()

    if hospitals.empty:
        return None

    if "hospital_id" not in hospitals.columns:
        return None

    hospital_id = str(
        hospital_id
    ).strip()

    rows = hospitals[
        hospitals["hospital_id"]
        .astype(str)
        .str.strip()
        == hospital_id
    ]

    if rows.empty:
        return None

    return rows.iloc[0]


# =========================================================
# PREDICTION RESULTS
# =========================================================

def get_predictions(patient_id):

    predictions = load_csv(
        PREDICTION_FILE
    )

    if predictions.empty:
        return predictions

    if "patient_id" not in predictions.columns:
        return pd.DataFrame()

    patient_id = str(
        patient_id
    ).strip()

    predictions["patient_id"] = (
        predictions["patient_id"]
        .astype(str)
        .str.strip()
    )

    return predictions[
        predictions["patient_id"]
        == patient_id
    ].copy()


# =========================================================
# PATIENT REPORT
# =========================================================

def get_report(patient_id):

    if not os.path.exists(
        REPORT_FILE
    ):
        return None

    try:

        with open(
            REPORT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            reports = json.load(file)

        return reports.get(
            str(patient_id)
        )

    except Exception:

        return None


# =========================================================
# COMPLETE EHR
# =========================================================

def get_complete_ehr(
    patient_id
):

    patient = get_patient(
        patient_id
    )

    if patient is None:
        return None

    admissions = get_admissions(
        patient_id
    )

    diagnoses = get_diagnoses(
        patient_id
    )

    billing = get_billing(
        patient_id
    )

    predictions = get_predictions(
        patient_id
    )

    report = get_report(
        patient_id
    )

    # -----------------------------------------------------
    # HOSPITALS ASSOCIATED WITH ADMISSIONS
    # -----------------------------------------------------

    hospital_records = []

    if (
        not admissions.empty
        and "hospital_id"
        in admissions.columns
    ):

        hospital_ids = (
            admissions["hospital_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        for hospital_id in hospital_ids:

            hospital = (
                get_hospital_for_admission(
                    hospital_id
                )
            )

            if hospital is not None:

                hospital_records.append(
                    hospital
                )

    if hospital_records:

        hospitals = pd.DataFrame(
            hospital_records
        )

    else:

        hospitals = pd.DataFrame()

    return {

        "patient": patient,

        "admissions": admissions,

        "diagnoses": diagnoses,

        "billing": billing,

        "hospitals": hospitals,

        "predictions": predictions,

        "report": report
    }