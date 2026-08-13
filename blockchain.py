import os
import json
import hashlib
from datetime import datetime


# =========================================================
# PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BLOCKCHAIN_FILE = os.path.join(
    BASE_DIR,
    "blockchain.json"
)


# =========================================================
# HASH
# =========================================================

def calculate_hash(data):

    encoded = json.dumps(
        data,
        sort_keys=True,
        default=str
    ).encode("utf-8")

    return hashlib.sha256(
        encoded
    ).hexdigest()


# =========================================================
# LOAD BLOCKCHAIN
# =========================================================

def load_blockchain():

    if not os.path.exists(
        BLOCKCHAIN_FILE
    ):

        return []

    try:

        with open(
            BLOCKCHAIN_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except Exception:

        return []


# =========================================================
# SAVE BLOCKCHAIN
# =========================================================

def save_blockchain(chain):

    with open(
        BLOCKCHAIN_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chain,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# CREATE BLOCK
# =========================================================

def create_block(
    record_type,
    record_data
):

    chain = load_blockchain()

    block_index = len(chain)

    previous_hash = (
        chain[-1]["hash"]
        if chain
        else "0"
    )

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    patient_id = str(
        record_data.get(
            "patient_id",
            ""
        )
    )

    created_by = str(
        record_data.get(
            "created_by",
            "System"
        )
    )

    record_data_hash = calculate_hash(
        record_data
    )

    block = {

        "block_index":
            block_index,

        "patient_id":
            patient_id,

        "record_type":
            str(record_type),

        "created_by":
            created_by,

        "timestamp":
            timestamp,

        "previous_hash":
            previous_hash,

        "record_data_hash":
            record_data_hash
    }

    block["hash"] = calculate_hash(
        block
    )

    chain.append(block)

    save_blockchain(chain)

    return block


# =========================================================
# VERIFY BLOCKCHAIN
# =========================================================

def verify_blockchain():

    chain = load_blockchain()

    if not chain:

        return (
            True,
            "Blockchain is empty. No records to verify."
        )

    for index, block in enumerate(chain):

        # -------------------------------------------------
        # Check index
        # -------------------------------------------------

        if block.get(
            "block_index"
        ) != index:

            return (
                False,
                f"Invalid block index at block {index}."
            )

        # -------------------------------------------------
        # Check previous hash
        # -------------------------------------------------

        expected_previous = (
            chain[index - 1]["hash"]
            if index > 0
            else "0"
        )

        if block.get(
            "previous_hash"
        ) != expected_previous:

            return (
                False,
                f"Previous hash mismatch at block {index}."
            )

        # -------------------------------------------------
        # Recalculate block hash
        # -------------------------------------------------

        block_without_hash = {
            key: value
            for key, value in block.items()
            if key != "hash"
        }

        expected_hash = calculate_hash(
            block_without_hash
        )

        if block.get(
            "hash"
        ) != expected_hash:

            return (
                False,
                f"Tampering detected at block {index}."
            )

    return (
        True,
        "Blockchain integrity verified successfully."
    )


# =========================================================
# PATIENT BLOCKS
# =========================================================

def get_patient_blocks(
    patient_id
):

    patient_id = str(
        patient_id
    ).strip()

    chain = load_blockchain()

    return [

        block

        for block in chain

        if str(
            block.get(
                "patient_id",
                ""
            )
        ).strip() == patient_id

    ]