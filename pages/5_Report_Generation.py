import os
from datetime import datetime

import pandas as pd
import streamlit as st

from auth import require_login


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | Report Generation",
    page_icon="📄",
    layout="wide"
)

require_login()


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


PATIENTS_FILE = os.path.join(
    BASE_DIR,
    "patients.csv"
)

PREDICTIONS_FILE = os.path.join(
    BASE_DIR,
    "prediction_results.csv"
)

ADMISSIONS_FILE = os.path.join(
    BASE_DIR,
    "admissions.csv"
)


# ============================================================
# LOAD CSV
# ============================================================

@st.cache_data
def load_csv(
    path,
    modified_time=None
):

    if not os.path.exists(path):

        return pd.DataFrame()

    try:

        return pd.read_csv(path)

    except Exception:

        return pd.DataFrame()


def get_mtime(path):

    if not os.path.exists(path):
        return None

    try:

        return os.path.getmtime(path)

    except Exception:

        return None


patients = load_csv(
    PATIENTS_FILE,
    get_mtime(
        PATIENTS_FILE
    )
)

predictions = load_csv(
    PREDICTIONS_FILE,
    get_mtime(
        PREDICTIONS_FILE
    )
)

admissions = load_csv(
    ADMISSIONS_FILE,
    get_mtime(
        ADMISSIONS_FILE
    )
)


# ============================================================
# NORMALIZE COLUMNS
# ============================================================

def normalize_columns(df):

    if df.empty:

        return df

    df = df.copy()

    df.columns = [

        str(column)
        .strip()
        .lower()
        .replace(
            " ",
            "_"
        )

        for column
        in df.columns

    ]

    return df


patients = normalize_columns(
    patients
)

predictions = normalize_columns(
    predictions
)

admissions = normalize_columns(
    admissions
)


# ============================================================
# NORMALIZE IDS
# ============================================================

for dataframe in [
    patients,
    predictions,
    admissions
]:

    if (
        not dataframe.empty
        and
        "patient_id"
        in dataframe.columns
    ):

        dataframe[
            "patient_id"
        ] = (
            dataframe[
                "patient_id"
            ]
            .astype(str)
            .str.strip()
        )


# ============================================================
# ROLE
# ============================================================

role = st.session_state.get(
    "role",
    ""
)


if role not in [
    "Doctor",
    "Admin",
    "Patient"
]:

    st.error(
        "You are not authorized to generate reports."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title(
    "📄 CareWatch-AI Report Generation"
)

st.caption(
    "Generate a clinical AI-assisted "
    "30-day readmission report."
)

st.markdown("---")


# ============================================================
# PATIENT SELECTION
# ============================================================

if role == "Patient":

    selected_patient = (
        st.session_state.get(
            "patient_id"
        )
    )


    if not selected_patient:

        st.error(
            "Patient ID could not be found."
        )

        st.stop()


    selected_patient = str(
        selected_patient
    ).strip()


    st.info(
        f"Patient Report: {selected_patient}"
    )


else:

    if (
        patients.empty
        or
        "patient_id"
        not in patients.columns
    ):

        st.error(
            "Patient data could not be loaded."
        )

        st.stop()


    patient_ids = sorted(
        patients[
            "patient_id"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    if not patient_ids:

        st.error(
            "No patients were found."
        )

        st.stop()


    previous_patient = (
        st.session_state.get(
            "selected_patient_id"
        )
    )


    default_index = 0


    if (
        previous_patient
        and
        str(previous_patient)
        in patient_ids
    ):

        default_index = (
            patient_ids.index(
                str(
                    previous_patient
                )
            )
        )


    selected_patient = st.selectbox(
        "Select Patient",
        patient_ids,
        index=default_index
    )


    st.session_state[
        "selected_patient_id"
    ] = selected_patient


patient_id = str(
    selected_patient
).strip()


# ============================================================
# FIND PATIENT
# ============================================================

patient = None


if (
    not patients.empty
    and
    "patient_id"
    in patients.columns
):

    patient_rows = patients[
        patients[
            "patient_id"
        ]
        ==
        patient_id
    ]


    if not patient_rows.empty:

        patient = (
            patient_rows.iloc[0]
        )


# ============================================================
# LATEST PREDICTION
# ============================================================

def find_latest_prediction(
    patient_id
):

    if (
        predictions.empty
        or
        "patient_id"
        not in predictions.columns
    ):

        return None


    data = predictions[
        predictions[
            "patient_id"
        ]
        ==
        patient_id
    ].copy()


    if data.empty:

        return None


    if (
        "timestamp"
        in data.columns
    ):

        data[
            "_prediction_time"
        ] = pd.to_datetime(
            data[
                "timestamp"
            ],
            errors="coerce"
        )


        if (
            data[
                "_prediction_time"
            ]
            .notna()
            .any()
        ):

            data = data.sort_values(
                "_prediction_time",
                ascending=False
            )

            return data.iloc[0]


    return data.iloc[-1]


prediction = find_latest_prediction(
    patient_id
)


if prediction is None:

    st.warning(
        "No AI prediction is available "
        "for this patient."
    )

    st.info(
        "Run the AI Readmission Prediction first. "
        "The generated report will then use the "
        "saved prediction from prediction_results.csv."
    )

    st.stop()


# ============================================================
# HELPER
# ============================================================

def get_value(
    row,
    columns,
    default=None
):

    if row is None:

        return default


    for column in columns:

        if column in row.index:

            value = row[
                column
            ]

            if pd.notna(
                value
            ):

                return value


    return default


# ============================================================
# PROBABILITY
# ============================================================

probability = get_value(
    prediction,
    [
        "risk_probability",
        "readmission_probability",
        "prediction_probability",
        "probability",
        "readmission_prob",
        "predicted_probability"
    ]
)


probability_value = None


try:

    probability_value = float(
        probability
    )

    probability_fraction = (
        probability_value
        if probability_value <= 1
        else probability_value / 100
    )

    probability_display = (
        f"{probability_fraction * 100:.2f}%"
    )

except Exception:

    probability_fraction = None

    probability_display = "N/A"


# ============================================================
# RISK LEVEL
# ============================================================

risk_level = get_value(
    prediction,
    [
        "risk_level",
        "risk",
        "risk_category"
    ]
)


if (
    risk_level is None
    and
    probability_fraction is not None
):

    if probability_fraction >= 0.70:

        risk_level = "High"

    elif probability_fraction >= 0.30:

        risk_level = "Moderate"

    else:

        risk_level = "Low"


if risk_level is None:

    risk_level = "Unknown"


# ============================================================
# BINARY THRESHOLD
# ============================================================

threshold = get_value(
    prediction,
    [
        "binary_threshold",
        "threshold"
    ],
    0.55
)


try:

    threshold = float(
        threshold
    )

except Exception:

    threshold = 0.55


# ============================================================
# BINARY READMISSION PREDICTION
# ============================================================

predicted_readmission = get_value(
    prediction,
    [
        "predicted_readmission"
    ]
)


readmission_label = get_value(
    prediction,
    [
        "readmission_label"
    ]
)


if (
    readmission_label is None
    and
    predicted_readmission is not None
):

    try:

        predicted_readmission = int(
            float(
                predicted_readmission
            )
        )

        readmission_label = (
            "Yes"
            if predicted_readmission == 1
            else "No"
        )

    except Exception:

        readmission_label = None


if (
    readmission_label is None
    and
    probability_fraction is not None
):

    predicted_readmission = int(
        probability_fraction
        >=
        threshold
    )

    readmission_label = (
        "Yes"
        if predicted_readmission == 1
        else "No"
    )


if readmission_label is None:

    readmission_label = "N/A"


# ============================================================
# PREDICTION DATE
# ============================================================

prediction_date = get_value(
    prediction,
    [
        "timestamp",
        "created_at",
        "prediction_date"
    ],
    datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)


# ============================================================
# DISPLAY PREDICTION
# ============================================================

st.subheader(
    "🤖 AI Readmission Prediction"
)


c1, c2, c3, c4 = st.columns(
    4
)


with c1:

    st.metric(
        "Patient ID",
        patient_id
    )


with c2:

    st.metric(
        "Risk Level",
        str(
            risk_level
        )
    )


with c3:

    st.metric(
        "Readmission Probability",
        probability_display
    )


with c4:

    st.metric(
        "30-Day Readmission",
        str(
            readmission_label
        )
    )


st.caption(
    f"Final Class-Weighted LightGBM | "
    f"Binary decision threshold: {threshold:.2f}"
)


st.success(
    "Saved AI prediction found successfully."
)


# ============================================================
# PATIENT INFORMATION
# ============================================================

st.markdown("---")

st.subheader(
    "👤 Patient Information"
)


if patient is not None:

    patient_info = {}


    for column in [

        "patient_id",
        "age",
        "gender",
        "state",
        "insurance_type",
        "bpl_card",
        "comorbidity_count",
        "prev_admissions"

    ]:

        if column in patient.index:

            patient_info[
                column
                .replace(
                    "_",
                    " "
                )
                .title()
            ] = patient[
                column
            ]


    patient_df = pd.DataFrame(
        list(
            patient_info.items()
        ),
        columns=[
            "Information",
            "Value"
        ]
    )


    st.dataframe(
        patient_df,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "Patient demographic information "
        "was not found."
    )


# ============================================================
# ADMISSION SUMMARY
# ============================================================

st.markdown("---")

st.subheader(
    "🏥 Admission Summary"
)


patient_admissions = pd.DataFrame()


if (
    not admissions.empty
    and
    "patient_id"
    in admissions.columns
):

    patient_admissions = admissions[
        admissions[
            "patient_id"
        ]
        ==
        patient_id
    ].copy()


if not patient_admissions.empty:

    c1, c2, c3 = st.columns(
        3
    )


    with c1:

        st.metric(
            "Total Admissions",
            len(
                patient_admissions
            )
        )


    with c2:

        if (
            "los_days"
            in patient_admissions.columns
        ):

            los = pd.to_numeric(
                patient_admissions[
                    "los_days"
                ],
                errors="coerce"
            ).mean()


            st.metric(
                "Average Length of Stay",
                (
                    f"{los:.1f} days"
                    if pd.notna(los)
                    else "N/A"
                )
            )

        else:

            st.metric(
                "Average Length of Stay",
                "N/A"
            )


    with c3:

        previous = (
            patient.get(
                "prev_admissions",
                "N/A"
            )
            if patient is not None
            else "N/A"
        )


        st.metric(
            "Previous Admissions",
            previous
        )


else:

    st.info(
        "No admission history was found."
    )


# ============================================================
# CLINICAL SUMMARY
# ============================================================

st.markdown("---")

st.subheader(
    "🧠 Clinical Summary"
)


risk_lower = str(
    risk_level
).lower()


if "high" in risk_lower:

    summary = (
        "The CareWatch-AI model indicates a high "
        "readmission-risk probability for this patient. "
        "The result should be reviewed together with the "
        "patient's clinical condition and other relevant "
        "health information."
    )


elif "moderate" in risk_lower:

    summary = (
        "The CareWatch-AI model indicates a moderate "
        "readmission-risk probability for this patient. "
        "Clinical follow-up and relevant risk factors "
        "should be reviewed."
    )


else:

    summary = (
        "The CareWatch-AI model indicates a lower "
        "readmission-risk probability for this patient. "
        "Routine clinical monitoring and appropriate "
        "follow-up should continue."
    )


st.info(
    summary
)


# ============================================================
# MODEL DECISION
# ============================================================

st.subheader(
    "🎯 Model Decision"
)


if str(
    readmission_label
).lower() in [
    "yes",
    "1",
    "true"
]:

    st.warning(
        f"The predicted probability meets or exceeds "
        f"the model's {threshold:.2f} operating threshold. "
        f"The binary model output is therefore "
        f"'Predicted Readmission'."
    )


elif str(
    readmission_label
).lower() in [
    "no",
    "0",
    "false"
]:

    st.success(
        f"The predicted probability is below "
        f"the model's {threshold:.2f} operating threshold. "
        f"The binary model output is therefore "
        f"'No Predicted Readmission'."
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader(
    "💡 Recommendations"
)


recommendations = [

    "Review the AI assessment together with the patient's clinical record.",

    "Consider relevant clinical and administrative risk factors.",

    "Ensure appropriate follow-up based on the treating clinician's assessment.",

    "Use the AI output as decision support rather than as a replacement for professional clinical judgement."

]


for item in recommendations:

    st.write(
        f"✅ {item}"
    )


# ============================================================
# PDF
# ============================================================

def generate_pdf():

    try:

        from reportlab.lib import colors

        from reportlab.lib.pagesizes import A4

        from reportlab.lib.styles import (
            getSampleStyleSheet
        )

        from reportlab.lib.enums import (
            TA_CENTER
        )

        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
        )

    except ImportError:

        return (
            None,
            "ReportLab is not installed. "
            "Add reportlab to requirements.txt."
        )


    import io


    buffer = io.BytesIO()


    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )


    styles = (
        getSampleStyleSheet()
    )


    title_style = styles[
        "Title"
    ]

    title_style.alignment = (
        TA_CENTER
    )


    heading_style = styles[
        "Heading2"
    ]

    normal_style = styles[
        "BodyText"
    ]


    story = []


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "CAREWATCH-AI",
            title_style
        )
    )


    story.append(
        Paragraph(
            "Explainable AI-Based Clinical Decision Support System",
            styles[
                "Heading3"
            ]
        )
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    story.append(
        Paragraph(
            "Patient Clinical AI Report",
            heading_style
        )
    )


    story.append(
        Spacer(
            1,
            10
        )
    )


    # --------------------------------------------------------
    # PATIENT DETAILS
    # --------------------------------------------------------

    patient_table = [

        [
            "Patient ID",
            patient_id
        ],

        [
            "Age",
            str(
                patient.get(
                    "age",
                    "N/A"
                )
                if patient is not None
                else "N/A"
            )
        ],

        [
            "Gender",
            str(
                patient.get(
                    "gender",
                    "N/A"
                )
                if patient is not None
                else "N/A"
            )
        ],

        [
            "State",
            str(
                patient.get(
                    "state",
                    "N/A"
                )
                if patient is not None
                else "N/A"
            )
        ]

    ]


    table = Table(
        patient_table,
        colWidths=[
            150,
            330
        ]
    )


    table.setStyle(
        TableStyle(
            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.lightgrey
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )

            ]
        )
    )


    story.append(
        table
    )


    story.append(
        Spacer(
            1,
            20
        )
    )


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "AI Readmission Prediction",
            heading_style
        )
    )


    prediction_table = [

        [
            "Risk Level",
            str(
                risk_level
            )
        ],

        [
            "Readmission Probability",
            probability_display
        ],

        [
            "Predicted 30-Day Readmission",
            str(
                readmission_label
            )
        ],

        [
            "Binary Decision Threshold",
            f"{threshold:.2f}"
        ],

        [
            "Prediction Date",
            str(
                prediction_date
            )
        ],

        [
            "Model",
            "Class-Weighted LightGBM"
        ]

    ]


    table = Table(
        prediction_table,
        colWidths=[
            190,
            290
        ]
    )


    table.setStyle(
        TableStyle(
            [

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.lightgrey
                ),

                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )

            ]
        )
    )


    story.append(
        table
    )


    story.append(
        Spacer(
            1,
            20
        )
    )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Clinical Summary",
            heading_style
        )
    )


    story.append(
        Paragraph(
            summary,
            normal_style
        )
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Recommendations",
            heading_style
        )
    )


    for recommendation in recommendations:

        story.append(
            Paragraph(
                "• "
                +
                recommendation,
                normal_style
            )
        )

        story.append(
            Spacer(
                1,
                5
            )
        )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # --------------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "<b>Clinical Decision Support Notice</b>",
            heading_style
        )
    )


    story.append(
        Paragraph(
            "CareWatch-AI provides AI-assisted clinical "
            "decision support. The predicted probability, "
            "risk classification and binary prediction "
            "should not be interpreted as an independent "
            "medical diagnosis. Clinical decisions should "
            "always be made by qualified healthcare "
            "professionals using the complete patient record.",
            normal_style
        )
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    story.append(
        Paragraph(
            "Generated by CareWatch-AI",
            styles[
                "Italic"
            ]
        )
    )


    doc.build(
        story
    )


    buffer.seek(
        0
    )


    return (
        buffer.getvalue(),
        None
    )


# ============================================================
# DOWNLOAD PDF
# ============================================================

st.markdown("---")

st.subheader(
    "📄 Download Patient Report"
)


if st.button(
    "Generate PDF Report",
    type="primary",
    use_container_width=True
):

    pdf_bytes, error = (
        generate_pdf()
    )


    if error:

        st.error(
            error
        )


    else:

        filename = (
            f"CareWatch-AI_Report_"
            f"{patient_id}.pdf"
        )


        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True
        )


        st.success(
            "PDF report generated successfully."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "CareWatch-AI | Final Class-Weighted LightGBM | "
    "AI-Assisted Clinical Decision Support"
)