import streamlit as st
import pandas as pd
import os


# =========================================================
# CAREWATCH-AI AUTHENTICATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATIENT_FILE = os.path.join(BASE_DIR, "patients.csv")


# =========================================================
# FIXED DOCTOR / ADMIN ACCOUNTS
# =========================================================

DOCTOR_USERNAME = "doctor"
DOCTOR_PASSWORD = "doctor123"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

PATIENT_PASSWORD = "patient123"


# =========================================================
# LOAD PATIENT IDs
# =========================================================

@st.cache_data
def load_patient_ids():

    if not os.path.exists(PATIENT_FILE):
        return set()

    try:

        df = pd.read_csv(PATIENT_FILE)

        if "patient_id" not in df.columns:
            return set()

        return set(
            df["patient_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

    except Exception:

        return set()


PATIENT_IDS = load_patient_ids()


# =========================================================
# SESSION INITIALIZATION
# =========================================================

def initialize_session():

    defaults = {
        "logged_in": False,
        "username": None,
        "role": None,
        "patient_id": None,
        "name": None,
        "language": "English"
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


initialize_session()


# =========================================================
# LOGIN
# =========================================================

def login(username, password):

    username = str(username).strip()
    password = str(password)

    # -----------------------------------------------------
    # VERY IMPORTANT:
    # Clear previous user's session first.
    # This prevents Patient -> Admin/Doctor role leakage.
    # -----------------------------------------------------

    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.patient_id = None
    st.session_state.name = None

    # =====================================================
    # DOCTOR
    # =====================================================

    if (
        username.lower() == DOCTOR_USERNAME
        and password == DOCTOR_PASSWORD
    ):

        st.session_state.logged_in = True
        st.session_state.username = DOCTOR_USERNAME
        st.session_state.role = "Doctor"
        st.session_state.patient_id = None
        st.session_state.name = "Dr. CareWatch"

        return True, "Doctor login successful."

    # =====================================================
    # ADMIN
    # =====================================================

    if (
        username.lower() == ADMIN_USERNAME
        and password == ADMIN_PASSWORD
    ):

        st.session_state.logged_in = True
        st.session_state.username = ADMIN_USERNAME
        st.session_state.role = "Admin"
        st.session_state.patient_id = None
        st.session_state.name = "System Administrator"

        return True, "Admin login successful."

    # =====================================================
    # PATIENT
    # =====================================================

    # Patient username MUST be a real UUID from patients.csv

    if username in PATIENT_IDS:

        if password != PATIENT_PASSWORD:

            return False, "Invalid patient password."

        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = "Patient"

        # Store the exact UUID
        st.session_state.patient_id = username

        st.session_state.name = "Patient"

        return True, "Patient login successful."

    # =====================================================
    # INVALID LOGIN
    # =====================================================

    return False, "Invalid username or password."


# =========================================================
# LOGIN PAGE
# =========================================================

def show_login():

    initialize_session()

    # -----------------------------------------------------
    # Hide sidebar
    # -----------------------------------------------------

    st.markdown(
        """
        <style>

        [data-testid="stSidebar"] {
            display: none;
        }

        .login-box {
            max-width: 520px;
            margin: 60px auto;
            padding: 35px;
            border-radius: 18px;
            border: 1px solid rgba(128,128,128,0.25);
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # Logo
    # -----------------------------------------------------

    logo_candidates = [
        os.path.join(BASE_DIR, "assets", "logo.png"),
        os.path.join(BASE_DIR, "assets", "carewatch_logo.png"),
        os.path.join(BASE_DIR, "assets", "CareWatch-AI.png"),
    ]

    logo_path = None

    for path in logo_candidates:

        if os.path.exists(path):
            logo_path = path
            break

    if logo_path:

        c1, c2, c3 = st.columns([1, 2, 1])

        with c2:

            st.image(
                logo_path,
                use_container_width=True
            )

    else:

        st.markdown(
            "<div style='text-align:center;font-size:60px;'>🩺</div>",
            unsafe_allow_html=True
        )

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    st.markdown(
        """
        <h1 style="text-align:center;">
        CareWatch-AI
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style="text-align:center;">
        AI-Based Clinical Decision Support System
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # =====================================================
    # LOGIN FORM
    # =====================================================

    with st.form("login_form"):

        username = st.text_input(
            "Username / Patient ID",
            placeholder="Doctor username, Admin username or Patient UUID"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "🔐 Login",
            use_container_width=True
        )

        if submitted:

            if not username or not password:

                st.error(
                    "Please enter username and password."
                )

            else:

                success, message = login(
                    username,
                    password
                )

                if success:

                    st.success(message)

                    st.rerun()

                else:

                    st.error(message)

    # =====================================================
    # DEMO CREDENTIALS
    # =====================================================

    with st.expander("Login Information"):

        st.markdown(
            """
            ### 👨‍⚕️ Doctor

            **Username:** `doctor`

            **Password:** `doctor123`

            ---

            ### 👨‍💼 Admin

            **Username:** `admin`

            **Password:** `admin123`

            ---

            ### 👤 Patient

            **Username:** Your actual `patient_id` from `patients.csv`

            **Password:** `patient123`

            Example:

            `ab3bda6c-05df-4f4f-a6b2-c98e7dfcf336`

            **Patient password:** `patient123`
            """
        )

    st.markdown("---")

    st.caption(
        "CareWatch-AI | Secure Clinical Decision Support System"
    )


# =========================================================
# CHECK LOGIN
# =========================================================

def is_logged_in():

    return bool(
        st.session_state.get(
            "logged_in",
            False
        )
    )


# =========================================================
# REQUIRE LOGIN
# =========================================================

def require_login():

    initialize_session()

    if not is_logged_in():

        show_login()

        st.stop()

    return True


# =========================================================
# REQUIRE ROLE
# =========================================================

def require_role(allowed_roles):

    require_login()

    if isinstance(allowed_roles, str):

        allowed_roles = [allowed_roles]

    current_role = st.session_state.get(
        "role"
    )

    if current_role not in allowed_roles:

        st.error(
            "You are not authorized to access this page."
        )

        st.stop()

    return True


# =========================================================
# GET ROLE
# =========================================================

def get_role():

    return st.session_state.get(
        "role"
    )


# =========================================================
# GET USERNAME
# =========================================================

def get_username():

    return st.session_state.get(
        "username"
    )


# =========================================================
# GET PATIENT ID
# =========================================================

def get_patient_id():

    patient_id = st.session_state.get(
        "patient_id"
    )

    if patient_id:

        return str(patient_id).strip()

    return None


# =========================================================
# SET PATIENT ID
# =========================================================

def set_patient_id(patient_id):

    if patient_id is None:

        st.session_state.patient_id = None

    else:

        st.session_state.patient_id = (
            str(patient_id).strip()
        )


# =========================================================
# LOGOUT
# =========================================================

def logout():

    # Completely remove authentication state

    for key in [
        "logged_in",
        "username",
        "role",
        "patient_id",
        "name",
        "language"
    ]:

        if key in st.session_state:

            del st.session_state[key]

    initialize_session()

    st.rerun()


# =========================================================
# ROLE LANDING
# =========================================================

def redirect_after_login():

    require_login()

    role = st.session_state.get(
        "role"
    )

    name = st.session_state.get(
        "name",
        ""
    )

    # =====================================================
    # DOCTOR
    # =====================================================

    if role == "Doctor":

        st.title("🩺 CareWatch-AI")

        st.subheader(
            f"Welcome, {name}"
        )

        st.success(
            "Doctor Portal"
        )

        st.info(
            "Select a Doctor feature from the sidebar."
        )

    # =====================================================
    # PATIENT
    # =====================================================

    elif role == "Patient":

        st.title("🩺 CareWatch-AI")

        st.subheader(
            "Welcome, Patient"
        )

        st.success(
            "Patient Portal"
        )

        st.info(
            "Select your Patient Dashboard or EHR from the sidebar."
        )

    # =====================================================
    # ADMIN
    # =====================================================

    elif role == "Admin":

        st.title("🩺 CareWatch-AI")

        st.subheader(
            f"Welcome, {name}"
        )

        st.success(
            "Administrator Portal"
        )

        st.info(
            "Select an administration feature from the sidebar."
        )

    else:

        st.error(
            "Invalid user role."
        )

        logout()


# =========================================================
# SIDEBAR
# =========================================================

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

        # =================================================
        # DOCTOR
        # =================================================

        if role == "Doctor":

            st.markdown(
                "### 👨‍⚕️ Doctor"
            )

            st.page_link(
                "pages/1_Doctor_Dashboard.py",
                label="📊 Dashboard"
            )

            st.page_link(
                "pages/2_Prediction.py",
                label="🧠 AI Prediction"
            )

            st.page_link(
                "pages/3_EHR.py",
                label="📋 EHR"
            )

            st.page_link(
                "pages/4_SHAP_XAI.py",
                label="🔬 SHAP / XAI"
            )

        # =================================================
        # PATIENT
        # =================================================

        elif role == "Patient":

            st.markdown(
                "### 👤 Patient"
            )

            st.page_link(
                "pages/5_Patient_Dashboard.py",
                label="🏠 My Dashboard"
            )

            st.page_link(
                "pages/3_EHR.py",
                label="📋 My EHR"
            )

        # =================================================
        # ADMIN
        # =================================================

        elif role == "Admin":

            st.markdown(
                "### 👨‍💼 Administration"
            )

            st.page_link(
                "pages/6_Admin_Dashboard.py",
                label="📊 Admin Dashboard"
            )

            st.page_link(
                "pages/7_System_Management.py",
                label="👥 System Management"
            )

        st.markdown("---")

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            logout()


# =========================================================
# SHOW SIDEBAR FOR LOGGED-IN USERS
# =========================================================

if is_logged_in():

    show_sidebar()