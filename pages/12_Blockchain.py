import streamlit as st
import pandas as pd

from auth import require_role
from blockchain import (
    load_blockchain,
    verify_blockchain,
    get_patient_blocks
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareWatch-AI | Blockchain",
    page_icon="🔗",
    layout="wide"
)


# ============================================================
# ACCESS CONTROL
# ============================================================

require_role(["Doctor", "Admin"])


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_payload(block):

    if not isinstance(block, dict):
        return {}

    for key in [
        "data",
        "record",
        "payload"
    ]:

        value = block.get(key)

        if isinstance(value, dict):
            return value

    return block


def get_block_value(
    block,
    key,
    default="N/A"
):

    if not isinstance(block, dict):
        return default

    # First try top-level block
    value = block.get(key)

    if value not in [
        None,
        ""
    ]:
        return value

    # Then try nested payload
    payload = get_payload(block)

    value = payload.get(key)

    if value not in [
        None,
        ""
    ]:
        return value

    return default


def shorten_hash(value):

    if value is None:
        return "N/A"

    value = str(value)

    if len(value) <= 20:
        return value

    return value[:16] + "..."


# ============================================================
# HEADER
# ============================================================

st.title(
    "🔗 Blockchain Audit Ledger"
)

st.caption(
    "Tamper-evident audit trail for "
    "CareWatch-AI healthcare and AI prediction records."
)

st.markdown("---")


# ============================================================
# BLOCKCHAIN STATUS
# ============================================================

st.header(
    "🔐 Ledger Integrity"
)


try:

    valid, message = verify_blockchain()

    if valid:

        st.success(
            f"✅ {message}"
        )

    else:

        st.error(
            f"🚨 {message}"
        )

except Exception as error:

    valid = False

    st.error(
        "Unable to verify the blockchain ledger."
    )

    st.caption(
        f"Technical information: {error}"
    )


# ============================================================
# LOAD CHAIN
# ============================================================

try:

    chain = load_blockchain()

    if not isinstance(chain, list):
        chain = []

except Exception as error:

    chain = []

    st.error(
        "Unable to load the blockchain ledger."
    )

    st.caption(
        f"Technical information: {error}"
    )


# ============================================================
# LEDGER OVERVIEW
# ============================================================

patient_ids = set()

prediction_records = 0


for block in chain:

    if not isinstance(block, dict):
        continue

    patient_id = get_block_value(
        block,
        "patient_id",
        ""
    )

    if (
        patient_id
        and
        patient_id != "N/A"
    ):

        patient_ids.add(
            str(patient_id).strip()
        )


    record_type = str(
        get_block_value(
            block,
            "record_type",
            ""
        )
    ).lower()


    if "prediction" in record_type:

        prediction_records += 1


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Blocks",
        len(chain)
    )


with col2:

    st.metric(
        "Patients",
        len(patient_ids)
    )


with col3:

    st.metric(
        "Audit Records",
        len(chain)
    )


with col4:

    st.metric(
        "AI Prediction Records",
        prediction_records
    )


# ============================================================
# LEDGER STATUS MESSAGE
# ============================================================

if valid:

    st.info(
        "🔒 The blockchain ledger passed the "
        "current integrity verification."
    )

else:

    st.warning(
        "⚠️ Review the ledger integrity warning "
        "before relying on blockchain audit records."
    )


# ============================================================
# PATIENT SEARCH
# ============================================================

st.markdown("---")

st.header(
    "👤 Patient Blockchain Records"
)


# ------------------------------------------------------------
# PATIENT SELECTOR
# ------------------------------------------------------------

available_patient_ids = sorted(
    patient_ids
)


if available_patient_ids:

    patient_id = st.selectbox(
        "Select Patient ID",
        available_patient_ids
    )

else:

    patient_id = st.text_input(
        "Enter Patient ID",
        placeholder="Example: P001"
    )


# ============================================================
# PATIENT BLOCKS
# ============================================================

if patient_id:

    patient_id = str(
        patient_id
    ).strip()


    try:

        blocks = get_patient_blocks(
            patient_id
        )

    except Exception as error:

        blocks = []

        st.error(
            "Unable to retrieve blockchain "
            "records for this patient."
        )

        st.caption(
            f"Technical information: {error}"
        )


    if not blocks:

        st.warning(
            "No blockchain records were found "
            "for this Patient ID."
        )


    else:

        st.success(
            f"{len(blocks)} blockchain "
            f"record(s) found for {patient_id}."
        )


        display_data = []


        for block in blocks:

            if not isinstance(
                block,
                dict
            ):
                continue


            display_data.append(
                {

                    "Block":
                        get_block_value(
                            block,
                            "block_index",
                            get_block_value(
                                block,
                                "index",
                                "N/A"
                            )
                        ),

                    "Patient ID":
                        get_block_value(
                            block,
                            "patient_id"
                        ),

                    "Record Type":
                        get_block_value(
                            block,
                            "record_type"
                        ),

                    "Created By":
                        get_block_value(
                            block,
                            "created_by"
                        ),

                    "Timestamp":
                        get_block_value(
                            block,
                            "timestamp"
                        ),

                    "Previous Hash":
                        get_block_value(
                            block,
                            "previous_hash"
                        ),

                    "Record Hash":
                        get_block_value(
                            block,
                            "record_data_hash"
                        ),

                    "Block Hash":
                        get_block_value(
                            block,
                            "hash"
                        )
                }
            )


        if display_data:

            df = pd.DataFrame(
                display_data
            )


            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


        # ====================================================
        # LATEST BLOCK DETAILS
        # ====================================================

        st.subheader(
            "🔎 Latest Audit Record"
        )


        latest_block = blocks[-1]

        payload = get_payload(
            latest_block
        )


        c1, c2, c3 = st.columns(3)


        with c1:

            st.metric(
                "Block",
                str(
                    get_block_value(
                        latest_block,
                        "block_index",
                        get_block_value(
                            latest_block,
                            "index",
                            "N/A"
                        )
                    )
                )
            )


        with c2:

            st.metric(
                "Record Type",
                str(
                    get_block_value(
                        latest_block,
                        "record_type"
                    )
                )
            )


        with c3:

            st.metric(
                "Created By",
                str(
                    get_block_value(
                        latest_block,
                        "created_by"
                    )
                )
            )


        # ====================================================
        # AI PREDICTION AUDIT INFORMATION
        # ====================================================

        risk_level = payload.get(
            "risk_level"
        )

        risk_probability = payload.get(
            "risk_probability",
            payload.get(
                "readmission_probability"
            )
        )

        readmission_label = payload.get(
            "readmission_label"
        )

        predicted_readmission = payload.get(
            "predicted_readmission"
        )

        binary_threshold = payload.get(
            "binary_threshold"
        )


        prediction_data_available = any(
            value is not None
            for value in [
                risk_level,
                risk_probability,
                readmission_label,
                predicted_readmission,
                binary_threshold
            ]
        )


        if prediction_data_available:

            st.subheader(
                "🤖 Audited AI Prediction"
            )


            p1, p2, p3, p4 = st.columns(4)


            with p1:

                st.metric(
                    "Risk Level",
                    str(
                        risk_level
                        if risk_level is not None
                        else "N/A"
                    )
                )


            with p2:

                probability_display = "N/A"

                try:

                    probability_value = float(
                        risk_probability
                    )

                    if probability_value <= 1:

                        probability_value *= 100

                    probability_display = (
                        f"{probability_value:.2f}%"
                    )

                except Exception:

                    pass


                st.metric(
                    "Readmission Probability",
                    probability_display
                )


            with p3:

                if (
                    readmission_label is None
                    and
                    predicted_readmission is not None
                ):

                    try:

                        predicted_value = int(
                            float(
                                predicted_readmission
                            )
                        )

                        readmission_label = (
                            "Yes"
                            if predicted_value == 1
                            else "No"
                        )

                    except Exception:

                        readmission_label = "N/A"


                st.metric(
                    "30-Day Readmission",
                    str(
                        readmission_label
                        if readmission_label is not None
                        else "N/A"
                    )
                )


            with p4:

                try:

                    threshold_display = (
                        f"{float(binary_threshold):.2f}"
                    )

                except Exception:

                    threshold_display = "N/A"


                st.metric(
                    "Model Threshold",
                    threshold_display
                )


        # ====================================================
        # HASH DETAILS
        # ====================================================

        with st.expander(
            "🔐 View Cryptographic Hashes"
        ):

            st.write(
                "**Previous Block Hash**"
            )

            st.code(
                str(
                    get_block_value(
                        latest_block,
                        "previous_hash"
                    )
                ),
                language="text"
            )


            st.write(
                "**Record Data Hash**"
            )

            st.code(
                str(
                    get_block_value(
                        latest_block,
                        "record_data_hash"
                    )
                ),
                language="text"
            )


            st.write(
                "**Block Hash**"
            )

            st.code(
                str(
                    get_block_value(
                        latest_block,
                        "hash"
                    )
                ),
                language="text"
            )


# ============================================================
# COMPLETE LEDGER
# ============================================================

st.markdown("---")

st.header(
    "📚 Complete Audit Ledger"
)


if chain:

    ledger_data = []


    for block in chain:

        if not isinstance(
            block,
            dict
        ):
            continue


        ledger_data.append(
            {

                "Block":
                    get_block_value(
                        block,
                        "block_index",
                        get_block_value(
                            block,
                            "index",
                            "N/A"
                        )
                    ),

                "Patient ID":
                    get_block_value(
                        block,
                        "patient_id"
                    ),

                "Record":
                    get_block_value(
                        block,
                        "record_type"
                    ),

                "Created By":
                    get_block_value(
                        block,
                        "created_by"
                    ),

                "Timestamp":
                    get_block_value(
                        block,
                        "timestamp"
                    ),

                "Hash":
                    shorten_hash(
                        get_block_value(
                            block,
                            "hash"
                        )
                    )
            }
        )


    if ledger_data:

        ledger_df = pd.DataFrame(
            ledger_data
        )


        st.dataframe(
            ledger_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No readable blockchain records "
            "are available."
        )


else:

    st.info(
        "No blockchain records have been created yet."
    )


# ============================================================
# EXPLANATION
# ============================================================

st.markdown("---")

st.header(
    "ℹ️ How CareWatch-AI Blockchain Works"
)


st.markdown(
    """
### 1️⃣ Clinical data remains in the EHR

Patient medical information remains in the CareWatch-AI
clinical data and EHR system.

### 2️⃣ A digital fingerprint is generated

Relevant audit information is converted into a
cryptographic SHA-256 hash.

### 3️⃣ The audit record is stored in a block

The blockchain audit record can contain information such as:

- Patient ID
- Record type
- Timestamp
- User who created the record
- Record-data hash
- Previous block hash
- Current block hash

### 4️⃣ Blocks are cryptographically linked

Each block references the hash of the previous block.
Changing an earlier block therefore affects the integrity
of the chain.

### 5️⃣ Ledger integrity is verified

CareWatch-AI recalculates the required hashes and checks
the relationship between blockchain records.

If stored blockchain information has been altered,
integrity verification can identify the inconsistency.

### 6️⃣ AI predictions can be audited

Prediction audit records can preserve a cryptographic
reference to the prediction event, helping provide
traceability for the CareWatch-AI clinical workflow.
"""
)


# ============================================================
# SECURITY NOTICE
# ============================================================

st.markdown("---")

st.info(
    "🔒 Blockchain audit information is restricted "
    "to authorized Doctor and Admin users."
)

st.caption(
    "CareWatch-AI | Tamper-Evident Clinical Audit System"
)