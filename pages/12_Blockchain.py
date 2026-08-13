import streamlit as st
import pandas as pd

from auth import require_role, logout
from blockchain import (
    load_blockchain,
    verify_blockchain,
    get_patient_blocks
)


# =========================================================
# ACCESS CONTROL
# =========================================================

require_role(["Doctor", "Admin"])


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareWatch-AI | Blockchain",
    page_icon="🔗",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("🔗 Blockchain Audit Ledger")

st.caption(
    "Tamper-evident audit trail for CareWatch-AI healthcare records."
)


st.markdown("---")


# =========================================================
# BLOCKCHAIN STATUS
# =========================================================

st.header("🔐 Ledger Integrity")


valid, message = verify_blockchain()


if valid:

    st.success(
        f"✅ {message}"
    )

else:

    st.error(
        f"🚨 {message}"
    )


# =========================================================
# LOAD CHAIN
# =========================================================

chain = load_blockchain()


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Blocks",
        len(chain)
    )


with col2:

    patient_count = len(
        set(
            block["patient_id"]
            for block in chain
        )
    )

    st.metric(
        "Patients",
        patient_count
    )


with col3:

    record_count = len(
        chain
    )

    st.metric(
        "Audit Records",
        record_count
    )


st.markdown("---")


# =========================================================
# PATIENT SEARCH
# =========================================================

st.header("👤 Patient Blockchain Records")


patient_id = st.text_input(
    "Enter Patient ID",
    placeholder="Enter patient UUID"
)


if patient_id:

    blocks = get_patient_blocks(
        patient_id.strip()
    )

    if not blocks:

        st.warning(
            "No blockchain records found for this Patient ID."
        )

    else:

        st.success(
            f"{len(blocks)} blockchain record(s) found."
        )

        display_data = []

        for block in blocks:

            display_data.append({

                "Block":
                    block["block_index"],

                "Patient ID":
                    block["patient_id"],

                "Record Type":
                    block["record_type"],

                "Created By":
                    block["created_by"],

                "Timestamp":
                    block["timestamp"],

                "Previous Hash":
                    block["previous_hash"],

                "Record Hash":
                    block["record_data_hash"],

                "Block Hash":
                    block["hash"]
            })


        df = pd.DataFrame(
            display_data
        )


        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# COMPLETE LEDGER
# =========================================================

st.markdown("---")

st.header("📚 Complete Audit Ledger")


if chain:

    ledger_data = []

    for block in chain:

        ledger_data.append({

            "Block":
                block["block_index"],

            "Patient ID":
                block["patient_id"],

            "Record":
                block["record_type"],

            "Created By":
                block["created_by"],

            "Timestamp":
                block["timestamp"],

            "Hash":
                block["hash"][:16] + "..."

        })


    st.dataframe(
        pd.DataFrame(ledger_data),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No blockchain records have been created yet."
    )


# =========================================================
# EXPLANATION
# =========================================================

st.markdown("---")

st.header("ℹ️ How CareWatch-AI Blockchain Works")

st.markdown(
"""
### 1. EHR stores the healthcare record

Patient medical information remains in the application's
EHR/data storage.

### 2. SHA-256 creates a digital fingerprint

A cryptographic hash is generated from the relevant record.

### 3. Blockchain stores the fingerprint

The hash is stored inside a block together with:

- Patient ID
- Record type
- Timestamp
- User who created the record
- Previous block hash
- Current block hash

### 4. Blocks are linked

Each block contains the hash of the previous block.

Therefore, modifying an earlier block breaks the chain.

### 5. Integrity verification

CareWatch-AI recalculates the hashes and checks the chain.

If a record has been modified, the system reports:

**Tampering detected.**
"""
)