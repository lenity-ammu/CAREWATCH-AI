import os

import pandas as pd
import streamlit as st

from auth import require_role, logout
from config.theme import apply_theme


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | Admin Analytics",
    page_icon="📊",
    layout="wide"
)

apply_theme()


# ============================================================
# ACCESS CONTROL
# ============================================================

require_role(["Admin"])


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PREDICTION_FILE = os.path.join(
    BASE_DIR,
    "prediction_results.csv"
)


# ============================================================
# SESSION
# ============================================================

username = st.session_state.get(
    "username",
    "Admin"
)


# ============================================================
# HEADER
# ============================================================

header_col, logout_col = st.columns(
    [5, 1]
)


with header_col:

    st.title(
        "🏥 CareWatch-AI"
    )

    st.caption(
        "AI-Based Clinical Decision Support System"
    )


with logout_col:

    st.write("")

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        logout()


st.divider()


st.title(
    "📊 Admin Analytics Dashboard"
)

st.success(
    f"Welcome, {username.title()}!"
)

st.write(
    "Monitor patient risk, readmission predictions "
    "and healthcare analytics."
)

st.divider()


# ============================================================
# LOAD PREDICTION DATA
# ============================================================

if not os.path.exists(
    PREDICTION_FILE
):

    st.warning(
        "No prediction data is available yet."
    )

    st.info(
        "Generate patient predictions first "
        "to populate the analytics dashboard."
    )

    st.stop()


try:

    results = pd.read_csv(
        PREDICTION_FILE
    )

except Exception as error:

    st.error(
        f"Unable to read prediction data: {error}"
    )

    st.stop()


# ============================================================
# CHECK REQUIRED COLUMN
# ============================================================

if (
    results.empty
    or
    "patient_id"
    not in results.columns
):

    st.error(
        "patient_id column is missing "
        "from prediction_results.csv"
    )

    st.stop()


# ============================================================
# CLEAN PATIENT IDS
# ============================================================

results[
    "patient_id"
] = (
    results[
        "patient_id"
    ]
    .astype(str)
    .str.strip()
)


# ============================================================
# NORMALIZE RISK LEVEL
# ============================================================

if (
    "risk_level"
    in results.columns
):

    results[
        "risk_level"
    ] = (
        results[
            "risk_level"
        ]
        .astype(str)
        .str.strip()
        .str.title()
    )


# ============================================================
# NORMALIZE READMISSION PROBABILITY
# ============================================================
# New prediction records may store:
# 32.45  -> already a percentage
#
# Older records may store:
# 0.3245 -> probability fraction
#
# Convert each row individually to a percentage in 0-100.
# ============================================================

if (
    "risk_probability"
    in results.columns
):

    probability_series = pd.to_numeric(
        results[
            "risk_probability"
        ],
        errors="coerce"
    )


elif (
    "readmission_probability"
    in results.columns
):

    probability_series = pd.to_numeric(
        results[
            "readmission_probability"
        ],
        errors="coerce"
    )


else:

    probability_series = pd.Series(
        [pd.NA] * len(results),
        index=results.index,
        dtype="Float64"
    )


results[
    "risk_probability"
] = probability_series.apply(
    lambda value:
    (
        value * 100
        if pd.notna(value)
        and 0 <= value <= 1
        else value
    )
)


results[
    "risk_probability"
] = pd.to_numeric(
    results[
        "risk_probability"
    ],
    errors="coerce"
).clip(
    lower=0,
    upper=100
)


# ============================================================
# NORMALIZE TIMESTAMP
# ============================================================

if (
    "timestamp"
    in results.columns
):

    results[
        "_prediction_time"
    ] = pd.to_datetime(
        results[
            "timestamp"
        ],
        errors="coerce"
    )

    results = results.sort_values(
        [
            "patient_id",
            "_prediction_time"
        ],
        ascending=[
            True,
            True
        ]
    )


# ============================================================
# USE LATEST PREDICTION PER PATIENT
# ============================================================

latest_results = (
    results
    .groupby(
        "patient_id",
        as_index=False
    )
    .tail(1)
    .reset_index(
        drop=True
    )
)


# ============================================================
# BASIC COUNTS
# ============================================================

total_patients = (
    latest_results[
        "patient_id"
    ]
    .nunique()
)


high_risk = 0
moderate_risk = 0
low_risk = 0


if (
    "risk_level"
    in latest_results.columns
):

    risk_lower = (
        latest_results[
            "risk_level"
        ]
        .astype(str)
        .str.strip()
        .str.lower()
    )


    high_risk = int(
        (
            risk_lower
            ==
            "high"
        ).sum()
    )


    moderate_risk = int(
        (
            risk_lower
            ==
            "moderate"
        ).sum()
    )


    low_risk = int(
        (
            risk_lower
            ==
            "low"
        ).sum()
    )


# ============================================================
# PREDICTED READMISSION COUNT
# ============================================================

predicted_readmission_count = 0


if (
    "predicted_readmission"
    in latest_results.columns
):

    binary_prediction = pd.to_numeric(
        latest_results[
            "predicted_readmission"
        ],
        errors="coerce"
    )

    predicted_readmission_count = int(
        (
            binary_prediction
            ==
            1
        ).sum()
    )


# ============================================================
# AVERAGE READMISSION RISK
# ============================================================

average_probability = 0.0


if (
    "risk_probability"
    in latest_results.columns
):

    valid_probability = (
        latest_results[
            "risk_probability"
        ]
        .dropna()
    )


    if not valid_probability.empty:

        average_probability = float(
            valid_probability.mean()
        )


# ============================================================
# KEY HEALTHCARE METRICS
# ============================================================

st.header(
    "📌 Key Healthcare Metrics"
)


c1, c2, c3, c4, c5, c6 = st.columns(
    6
)


with c1:

    st.metric(
        "👥 Total Patients",
        total_patients
    )


with c2:

    st.metric(
        "🔴 High Risk",
        high_risk
    )


with c3:

    st.metric(
        "🟠 Moderate Risk",
        moderate_risk
    )


with c4:

    st.metric(
        "🟢 Low Risk",
        low_risk
    )


with c5:

    st.metric(
        "⚠️ Predicted Readmission",
        predicted_readmission_count
    )


with c6:

    st.metric(
        "📊 Avg Readmission Risk",
        f"{average_probability:.2f}%"
    )


# ============================================================
# MODEL INFORMATION
# ============================================================

with st.expander(
    "ℹ️ Final Prediction Model"
):

    st.write(
        "**Model:** Class-Weighted LightGBM"
    )

    st.write(
        "**Number of Input Features:** 27"
    )

    st.write(
        "**Binary Readmission Threshold:** 0.55"
    )

    st.caption(
        "The 0.55 threshold determines the binary "
        "30-day readmission prediction. "
        "Low, Moderate and High risk levels are "
        "separate probability-based interface categories."
    )


st.divider()


# ============================================================
# RISK DISTRIBUTION
# ============================================================

st.header(
    "📊 Risk Distribution"
)


if (
    "risk_level"
    in latest_results.columns
):

    risk_counts = (
        latest_results[
            "risk_level"
        ]
        .value_counts()
    )


    risk_chart = pd.DataFrame(
        {
            "Risk Level":
                risk_counts.index,

            "Patients":
                risk_counts.values
        }
    )


    if not risk_chart.empty:

        st.bar_chart(
            risk_chart.set_index(
                "Risk Level"
            )
        )

    else:

        st.info(
            "No risk-level records are available."
        )


else:

    st.info(
        "Risk-level data is not available."
    )


st.divider()


# ============================================================
# READMISSION PROBABILITY DISTRIBUTION
# ============================================================

st.header(
    "📈 Readmission Probability"
)


if (
    "risk_probability"
    in latest_results.columns
):

    probability_data = (
        latest_results[
            [
                "patient_id",
                "risk_probability"
            ]
        ]
        .dropna(
            subset=[
                "risk_probability"
            ]
        )
        .copy()
    )


    probability_data[
        "risk_probability"
    ] = (
        probability_data[
            "risk_probability"
        ]
        .round(2)
    )


    probability_data = (
        probability_data
        .sort_values(
            "risk_probability",
            ascending=False
        )
        .head(20)
    )


    probability_data = (
        probability_data
        .rename(
            columns={
                "risk_probability":
                    "Readmission Risk (%)"
            }
        )
        .set_index(
            "patient_id"
        )
    )


    if not probability_data.empty:

        st.bar_chart(
            probability_data[
                "Readmission Risk (%)"
            ]
        )

    else:

        st.info(
            "No valid readmission probability "
            "values are available."
        )


else:

    st.info(
        "Readmission probability data "
        "is not available."
    )


st.divider()


# ============================================================
# HIGH-RISK PATIENTS
# ============================================================

st.header(
    "🔴 High-Risk Patients"
)


if (
    "risk_level"
    in latest_results.columns
):

    high_risk_patients = latest_results[
        latest_results[
            "risk_level"
        ]
        .astype(str)
        .str.lower()
        .eq(
            "high"
        )
    ].copy()


    if not high_risk_patients.empty:

        columns_to_show = [
            "patient_id",
            "risk_level",
            "risk_probability",
            "readmission_label",
            "predicted_readmission",
            "binary_threshold",
            "timestamp"
        ]


        available_columns = [
            column
            for column
            in columns_to_show
            if column
            in high_risk_patients.columns
        ]


        high_display = (
            high_risk_patients[
                available_columns
            ]
            .copy()
        )


        if (
            "risk_probability"
            in high_display.columns
        ):

            high_display[
                "risk_probability"
            ] = (
                high_display[
                    "risk_probability"
                ]
                .round(2)
            )


        high_display = (
            high_display
            .rename(
                columns={

                    "patient_id":
                        "Patient ID",

                    "risk_level":
                        "Risk Level",

                    "risk_probability":
                        "Readmission Risk (%)",

                    "readmission_label":
                        "30-Day Readmission",

                    "predicted_readmission":
                        "Binary Prediction",

                    "binary_threshold":
                        "Model Threshold",

                    "timestamp":
                        "Prediction Time"

                }
            )
        )


        st.dataframe(
            high_display,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.success(
            "No high-risk patients "
            "are currently identified."
        )


else:

    st.info(
        "Risk-level information is unavailable."
    )


st.divider()


# ============================================================
# COMPLETE PATIENT RISK OVERVIEW
# ============================================================

st.header(
    "📋 Patient Risk Overview"
)


columns_to_show = [
    "patient_id",
    "risk_level",
    "risk_probability",
    "readmission_label",
    "predicted_readmission",
    "binary_threshold",
    "timestamp"
]


available_columns = [
    column
    for column
    in columns_to_show
    if column
    in latest_results.columns
]


overview = (
    latest_results[
        available_columns
    ]
    .copy()
)


if (
    "risk_probability"
    in overview.columns
):

    overview[
        "risk_probability"
    ] = (
        overview[
            "risk_probability"
        ]
        .round(2)
    )


overview = overview.rename(
    columns={

        "patient_id":
            "Patient ID",

        "risk_level":
            "Risk Level",

        "risk_probability":
            "Readmission Risk (%)",

        "readmission_label":
            "30-Day Readmission",

        "predicted_readmission":
            "Binary Prediction",

        "binary_threshold":
            "Model Threshold",

        "timestamp":
            "Prediction Time"

    }
)


st.dataframe(
    overview,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# DATASET SUMMARY
# ============================================================

st.header(
    "📄 Prediction Dataset Summary"
)


c1, c2, c3 = st.columns(
    3
)


with c1:

    st.metric(
        "Prediction Records",
        len(
            results
        )
    )


with c2:

    st.metric(
        "Unique Patients",
        total_patients
    )


with c3:

    latest_timestamp = "N/A"

    if (
        "_prediction_time"
        in results.columns
    ):

        valid_dates = (
            results[
                "_prediction_time"
            ]
            .dropna()
        )


        if not valid_dates.empty:

            latest_timestamp = (
                valid_dates
                .max()
                .strftime(
                    "%Y-%m-%d %H:%M"
                )
            )


    st.metric(
        "Latest Prediction",
        latest_timestamp
    )


# ============================================================
# ANALYTICS EXPLANATION
# ============================================================

st.divider()

st.header(
    "ℹ️ Analytics Interpretation"
)


st.markdown(
    """
The Admin Analytics Dashboard summarizes the **latest saved
prediction for each patient**.

- **High / Moderate / Low Risk** represent the application's
  probability-based risk categories.
- **Predicted Readmission** represents the final binary
  Class-Weighted LightGBM decision.
- The binary decision uses the optimized **0.55 threshold**.
- **Average Readmission Risk** is calculated from normalized
  patient probability percentages and therefore remains
  within the valid **0–100% range**.
"""
)


# ============================================================
# ADMIN NOTICE
# ============================================================

st.divider()


st.warning(
    "⚠️ Analytics are generated from the available "
    "prediction records. These statistics are intended "
    "for healthcare system monitoring and decision support "
    "and should not be interpreted as independent "
    "clinical decisions."
)


st.caption(
    "CareWatch-AI | Administrator Analytics Portal"
)