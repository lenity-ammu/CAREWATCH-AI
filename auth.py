import os
import hashlib
import secrets

import pandas as pd
import streamlit as st


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

USERS_FILE = os.path.join(
    BASE_DIR,
    "users.csv"
)

PATIENT_FILE = os.path.join(
    BASE_DIR,
    "patients.csv"
)


# ============================================================
# PASSWORD SECURITY
# ============================================================

PBKDF2_ITERATIONS = 200000


def hash_password(password, salt=None):

    password = str(password)

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS
    ).hex()

    return salt, password_hash


def verify_password(
    password,
    salt,
    stored_hash
):

    try:

        _, calculated_hash = hash_password(
            password,
            salt
        )

        return secrets.compare_digest(
            calculated_hash,
            stored_hash
        )

    except Exception:

        return False


# ============================================================
# PASSWORD VALIDATION
# ============================================================

def validate_new_password(password):

    password = str(password)

    if len(password) < 8:

        return (
            False,
            "Password must contain at least 8 characters."
        )

    if not any(
        character.isalpha()
        for character in password
    ):

        return (
            False,
            "Password must contain at least one letter."
        )

    if not any(
        character.isdigit()
        for character in password
    ):

        return (
            False,
            "Password must contain at least one number."
        )

    return True, ""


# ============================================================
# EMPTY USER DATABASE
# ============================================================

def empty_users_dataframe():

    return pd.DataFrame(
        columns=[
            "username",
            "role",
            "patient_id",
            "name",
            "password_salt",
            "password_hash"
        ]
    )


# ============================================================
# LOAD USERS
# ============================================================

def load_users():

    if not os.path.exists(
        USERS_FILE
    ):

        return empty_users_dataframe()

    try:

        users = pd.read_csv(
            USERS_FILE,
            dtype=str
        ).fillna("")

        # ----------------------------------------------------
        # MIGRATE OLD PLAINTEXT PASSWORD FILE
        # ----------------------------------------------------

        if (
            "password" in users.columns
            and
            (
                "password_salt"
                not in users.columns
                or
                "password_hash"
                not in users.columns
            )
        ):

            salts = []
            hashes = []

            for password in users[
                "password"
            ].astype(str):

                salt, password_hash = (
                    hash_password(
                        password
                    )
                )

                salts.append(salt)
                hashes.append(password_hash)

            users[
                "password_salt"
            ] = salts

            users[
                "password_hash"
            ] = hashes

            users = users.drop(
                columns=["password"]
            )

            users.to_csv(
                USERS_FILE,
                index=False
            )

        # ----------------------------------------------------
        # ENSURE REQUIRED COLUMNS
        # ----------------------------------------------------

        required_columns = [
            "username",
            "role",
            "patient_id",
            "name",
            "password_salt",
            "password_hash"
        ]

        for column in required_columns:

            if column not in users.columns:
                users[column] = ""

        users = users[
            required_columns
        ].copy()

        users["username"] = (
            users["username"]
            .astype(str)
            .str.strip()
        )

        users["role"] = (
            users["role"]
            .astype(str)
            .str.strip()
        )

        users["patient_id"] = (
            users["patient_id"]
            .astype(str)
            .str.strip()
        )

        users["name"] = (
            users["name"]
            .astype(str)
            .str.strip()
        )

        return users

    except Exception:

        return empty_users_dataframe()


# ============================================================
# SAVE USERS
# ============================================================

def save_users(users):

    try:

        users.to_csv(
            USERS_FILE,
            index=False
        )

        return True

    except Exception:

        return False


# ============================================================
# LOAD VALID PATIENT IDS
# ============================================================

@st.cache_data
def load_patient_ids():

    if not os.path.exists(
        PATIENT_FILE
    ):

        return set()

    try:

        patients = pd.read_csv(
            PATIENT_FILE,
            usecols=[
                "patient_id"
            ],
            dtype=str
        )

        return set(
            patients[
                "patient_id"
            ]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

    except Exception:

        return set()


# ============================================================
# SESSION INITIALIZATION
# ============================================================

def initialize_session():

    defaults = {
        "logged_in": False,
        "authenticated": False,
        "username": None,
        "role": None,
        "patient_id": None,
        "name": None,
        "language": "English"
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[
                key
            ] = value


# ============================================================
# CLEAR AUTHENTICATION
# ============================================================

def clear_authentication():

    st.session_state[
        "logged_in"
    ] = False

    st.session_state[
        "authenticated"
    ] = False

    st.session_state[
        "username"
    ] = None

    st.session_state[
        "role"
    ] = None

    st.session_state[
        "patient_id"
    ] = None

    st.session_state[
        "name"
    ] = None


# ============================================================
# LOGIN
# ============================================================

def login(username, password):

    initialize_session()

    username = str(
        username
    ).strip()

    password = str(
        password
    )

    clear_authentication()

    users = load_users()

    if users.empty:

        return (
            False,
            "No user accounts are currently configured."
        )

    matched = users[
        users[
            "username"
        ].str.lower()
        ==
        username.lower()
    ]

    if matched.empty:

        return (
            False,
            "Invalid username or password."
        )

    user = matched.iloc[0]

    if not verify_password(
        password,
        str(
            user[
                "password_salt"
            ]
        ),
        str(
            user[
                "password_hash"
            ]
        )
    ):

        return (
            False,
            "Invalid username or password."
        )

    role = str(
        user[
            "role"
        ]
    ).strip()

    if role not in [
        "Admin",
        "Doctor",
        "Patient"
    ]:

        return (
            False,
            "Invalid user role."
        )

    patient_id = None

    if role == "Patient":

        patient_id = str(
            user[
                "patient_id"
            ]
        ).strip()

        if not patient_id:

            patient_id = username

        patient_ids = load_patient_ids()

        if (
            not patient_ids
            or
            patient_id
            not in patient_ids
        ):

            return (
                False,
                "Patient account is not linked "
                "to a valid patient record."
            )

    user_name = str(
        user[
            "name"
        ]
    ).strip()

    if not user_name:

        if role == "Doctor":
            user_name = "Doctor"

        elif role == "Admin":
            user_name = "System Administrator"

        else:
            user_name = "Patient"

    st.session_state[
        "logged_in"
    ] = True

    st.session_state[
        "authenticated"
    ] = True

    st.session_state[
        "username"
    ] = str(
        user[
            "username"
        ]
    )

    st.session_state[
        "role"
    ] = role

    st.session_state[
        "patient_id"
    ] = (
        patient_id
        if role == "Patient"
        else None
    )

    st.session_state[
        "name"
    ] = user_name

    return (
        True,
        f"{role} login successful."
    )


# ============================================================
# PATIENT SELF-REGISTRATION
# ============================================================

def register_patient(
    patient_id,
    password,
    confirm_password
):

    patient_id = str(
        patient_id
    ).strip()

    password = str(
        password
    )

    confirm_password = str(
        confirm_password
    )

    # --------------------------------------------------------
    # REQUIRED FIELDS
    # --------------------------------------------------------

    if (
        not patient_id
        or
        not password
        or
        not confirm_password
    ):

        return (
            False,
            "Please complete all registration fields."
        )

    # --------------------------------------------------------
    # PASSWORD MATCH
    # --------------------------------------------------------

    if password != confirm_password:

        return (
            False,
            "Passwords do not match."
        )

    valid_password, message = (
        validate_new_password(
            password
        )
    )

    if not valid_password:

        return (
            False,
            message
        )

    # --------------------------------------------------------
    # VERIFY PATIENT EXISTS
    # --------------------------------------------------------

    patient_ids = load_patient_ids()

    if not patient_ids:

        return (
            False,
            "Patient records are unavailable."
        )

    if patient_id not in patient_ids:

        return (
            False,
            "Patient ID was not found."
        )

    # --------------------------------------------------------
    # CHECK EXISTING ACCOUNT
    # --------------------------------------------------------

    users = load_users()

    if not users.empty:

        existing_username = (
            users[
                "username"
            ]
            .str.lower()
            ==
            patient_id.lower()
        )

        existing_patient = (
            users[
                "patient_id"
            ]
            ==
            patient_id
        )

        if (
            existing_username.any()
            or
            existing_patient.any()
        ):

            return (
                False,
                "An account has already been "
                "registered for this Patient ID."
            )

    # --------------------------------------------------------
    # CREATE PASSWORD HASH
    # --------------------------------------------------------

    salt, password_hash = (
        hash_password(
            password
        )
    )

    new_user = pd.DataFrame(
        [
            {
                "username":
                    patient_id,

                "role":
                    "Patient",

                "patient_id":
                    patient_id,

                "name":
                    "Patient",

                "password_salt":
                    salt,

                "password_hash":
                    password_hash
            }
        ]
    )

    users = pd.concat(
        [
            users,
            new_user
        ],
        ignore_index=True
    )

    if save_users(
        users
    ):

        return (
            True,
            "Patient account created successfully. "
            "You can now log in using your "
            "Patient ID and password."
        )

    return (
        False,
        "Unable to create the patient account."
    )


# ============================================================
# CHANGE OWN PASSWORD
# ============================================================

def change_password(
    username,
    current_password,
    new_password
):

    username = str(
        username
    ).strip()

    valid_password, message = (
        validate_new_password(
            new_password
        )
    )

    if not valid_password:

        return (
            False,
            message
        )

    users = load_users()

    matched_index = users[
        users[
            "username"
        ].str.lower()
        ==
        username.lower()
    ].index

    if len(
        matched_index
    ) == 0:

        return (
            False,
            "User account not found."
        )

    index = matched_index[0]

    current_salt = str(
        users.at[
            index,
            "password_salt"
        ]
    )

    current_hash = str(
        users.at[
            index,
            "password_hash"
        ]
    )

    if not verify_password(
        current_password,
        current_salt,
        current_hash
    ):

        return (
            False,
            "Current password is incorrect."
        )

    new_salt, new_hash = (
        hash_password(
            new_password
        )
    )

    users.at[
        index,
        "password_salt"
    ] = new_salt

    users.at[
        index,
        "password_hash"
    ] = new_hash

    if save_users(
        users
    ):

        return (
            True,
            "Password changed successfully."
        )

    return (
        False,
        "Unable to update password."
    )


# ============================================================
# LOGIN STATUS
# ============================================================

def is_logged_in():

    initialize_session()

    return bool(
        st.session_state.get(
            "logged_in",
            False
        )
    )


# ============================================================
# REQUIRE LOGIN
# ============================================================

def require_login():

    initialize_session()

    if not is_logged_in():

        st.error(
            "Please log in to access this page."
        )

        st.page_link(
            "pages/1Login.py",
            label="🔐 Open Login Page"
        )

        st.stop()

    return True


# ============================================================
# REQUIRE ROLE
# ============================================================

def require_role(allowed_roles):

    require_login()

    if isinstance(
        allowed_roles,
        str
    ):

        allowed_roles = [
            allowed_roles
        ]

    current_role = (
        st.session_state.get(
            "role"
        )
    )

    if (
        current_role
        not in allowed_roles
    ):

        st.error(
            "You are not authorized "
            "to access this page."
        )

        st.stop()

    return True


# ============================================================
# GETTERS
# ============================================================

def get_role():

    return st.session_state.get(
        "role"
    )


def get_username():

    return st.session_state.get(
        "username"
    )


def get_patient_id():

    patient_id = (
        st.session_state.get(
            "patient_id"
        )
    )

    if patient_id:

        return str(
            patient_id
        ).strip()

    return None


def set_patient_id(patient_id):

    if patient_id is None:

        st.session_state[
            "patient_id"
        ] = None

    else:

        st.session_state[
            "patient_id"
        ] = str(
            patient_id
        ).strip()


# ============================================================
# LOGOUT
# ============================================================

def logout():

    for key in [
        "logged_in",
        "authenticated",
        "username",
        "role",
        "patient_id",
        "name",
        "language",
        "last_prediction",
        "last_model_input",
        "selected_patient_id"
    ]:

        if key in st.session_state:

            del st.session_state[
                key
            ]

    initialize_session()

    st.rerun()


# ============================================================
# ROLE LANDING
# ============================================================

def redirect_after_login():

    require_login()

    role = st.session_state.get(
        "role"
    )

    name = st.session_state.get(
        "name",
        ""
    )

    if role == "Doctor":

        st.title(
            "🩺 CareWatch-AI"
        )

        st.subheader(
            f"Welcome, {name}"
        )

        st.success(
            "Doctor Portal"
        )

        st.info(
            "Select a clinical module "
            "from the sidebar."
        )

    elif role == "Patient":

        st.title(
            "🩺 CareWatch-AI"
        )

        st.subheader(
            f"Welcome, {name}"
        )

        st.success(
            "Patient Portal"
        )

        st.info(
            "Select your Patient Dashboard "
            "or EHR from the sidebar."
        )

    elif role == "Admin":

        st.title(
            "🩺 CareWatch-AI"
        )

        st.subheader(
            f"Welcome, {name}"
        )

        st.success(
            "Administrator Portal"
        )

        st.info(
            "Select an administration module "
            "from the sidebar."
        )

    else:

        st.error(
            "Invalid user role."
        )

        logout()


# ============================================================
# SIDEBAR
# ============================================================

def show_sidebar():

    require_login()

    role = st.session_state.get(
        "role"
    )

    with st.sidebar:

        st.markdown(
            "## 🩺 CareWatch-AI"
        )

        st.caption(
            f"Role: {role}"
        )

        st.markdown("---")

        # ----------------------------------------------------
        # DOCTOR
        # ----------------------------------------------------

        if role == "Doctor":

            st.markdown(
                "### 👨‍⚕️ Doctor"
            )

            st.page_link(
                "pages/1_Doctor_Dashboard.py",
                label="📊 Dashboard"
            )

            st.page_link(
                "pages/3_Prediction.py",
                label="🧠 AI Prediction"
            )

            st.page_link(
                "pages/11_EHR.py",
                label="📋 EHR"
            )

            st.page_link(
                "pages/4_SHAP_Explainability.py",
                label="🔬 SHAP / XAI"
            )

            st.page_link(
                "pages/12_Blockchain.py",
                label="🔗 Blockchain Audit"
            )

            st.page_link(
                "pages/5_Report_Generation.py",
                label="📄 Report Generation"
            )

        # ----------------------------------------------------
        # PATIENT
        # ----------------------------------------------------

        elif role == "Patient":

            st.markdown(
                "### 👤 Patient"
            )

            st.page_link(
                "pages/10_Patient_Dashboard.py",
                label="🏠 My Dashboard"
            )

            st.page_link(
                "pages/11_EHR.py",
                label="📋 My EHR"
            )

        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------

        elif role == "Admin":

            st.markdown(
                "### 👨‍💼 Administration"
            )

            st.page_link(
                "pages/7_Admin.py",
                label="⚙️ Administration"
            )

        st.markdown("---")

        # ----------------------------------------------------
        # CHANGE PASSWORD
        # ----------------------------------------------------

        with st.expander(
            "🔑 Change Password"
        ):

            current_password = (
                st.text_input(
                    "Current Password",
                    type="password",
                    key=(
                        "sidebar_current_password"
                    )
                )
            )

            new_password = (
                st.text_input(
                    "New Password",
                    type="password",
                    key=(
                        "sidebar_new_password"
                    )
                )
            )

            confirm_password = (
                st.text_input(
                    "Confirm New Password",
                    type="password",
                    key=(
                        "sidebar_confirm_password"
                    )
                )
            )

            if st.button(
                "Update Password",
                use_container_width=True,
                key=(
                    "sidebar_change_password"
                )
            ):

                if (
                    not current_password
                    or
                    not new_password
                    or
                    not confirm_password
                ):

                    st.warning(
                        "Please complete all "
                        "password fields."
                    )

                elif (
                    new_password
                    !=
                    confirm_password
                ):

                    st.error(
                        "New passwords do not match."
                    )

                else:

                    success, message = (
                        change_password(
                            st.session_state.get(
                                "username"
                            ),
                            current_password,
                            new_password
                        )
                    )

                    if success:

                        st.success(
                            message
                        )

                    else:

                        st.error(
                            message
                        )

        st.markdown("---")

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="carewatch_logout"
        ):

            logout()


# ============================================================
# INITIALIZE WHEN IMPORTED
# ============================================================

initialize_session()