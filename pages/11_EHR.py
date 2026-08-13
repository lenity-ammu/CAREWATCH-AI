import streamlit as st
import pandas as pd
import os
from io import BytesIO

from auth import require_login

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareWatch-AI | Electronic Health Record",
    page_icon="📋",
    layout="wide"
)

# =========================================================
# LOGIN
# =========================================================

require_login()

# =========================================================
# PATH
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# =========================================================
# LANGUAGE
# Patient language is used here.
# Doctor/Admin remain English.
# =========================================================

role = st.session_state.get("role", "Patient")

if role == "Patient":
    language = st.session_state.get("language", "English")
else:
    language = "English"


# =========================================================
# TRANSLATIONS
# =========================================================

TEXT = {

    "English": {
        "title": "📋 Electronic Health Record",
        "subtitle": "Secure longitudinal patient health record",
        "profile": "👤 Patient Profile",
        "history": "🏥 Admission History",
        "diagnosis": "🩺 Diagnosis History",
        "billing": "💰 Billing History",
        "hospital": "🏨 Hospital Information",
        "prediction": "🤖 AI Readmission Prediction",
        "blockchain": "🔗 Blockchain Audit Record",
        "report": "📄 EHR Report",
        "download": "⬇️ Download EHR Report (PDF)",
        "no_data": "No information was found for this patient.",
        "patient_id": "Patient ID",
        "age": "Age",
        "gender": "Gender",
        "state": "State",
        "insurance": "Insurance",
        "bpl": "BPL Card",
        "admissions": "Total Admissions",
        "latest": "Latest Admission",
        "avg_los": "Average Length of Stay",
        "readmissions": "30-Day Readmissions",
        "total_cost": "Total Cost",
        "subsidy": "Government Subsidy",
        "out_of_pocket": "Out-of-Pocket Cost",
        "secure": "🔒 This health information is available only to authorized users.",
        "select_patient": "Select Patient",
        "unauthorized": "You are not authorized to view this EHR.",
        "risk": "Risk Level",
        "probability": "Readmission Probability",
        "summary": "Clinical Summary",
        "recommendations": "Recommendations",
        "block": "Block",
        "record_type": "Record Type",
        "created_by": "Created By",
        "verified": "Blockchain integrity verified successfully.",
        "no_blockchain": "No blockchain audit record is available for this patient.",
        "pdf_title": "CareWatch-AI Electronic Health Record",
        "prepared": "Prepared",
        "comorbidity": "Comorbidity Count",
        "previous_admissions": "Previous Admissions",
        "hospital_name": "Hospital",
        "hospital_tier": "Hospital Tier",
        "beds": "Beds",
        "teaching": "Teaching Hospital"
    },

    "Tamil": {
        "title": "📋 மின்னணு சுகாதார பதிவு",
        "subtitle": "பாதுகாப்பான நோயாளர் சுகாதார பதிவு",
        "profile": "👤 நோயாளர் விவரம்",
        "history": "🏥 அனுமதி வரலாறு",
        "diagnosis": "🩺 நோயறிதல் வரலாறு",
        "billing": "💰 பில்லிங் வரலாறு",
        "hospital": "🏨 மருத்துவமனை தகவல்",
        "prediction": "🤖 AI மீண்டும் மருத்துவமனையில் சேர்க்கும் அபாயம்",
        "blockchain": "🔗 பிளாக்செயின் தணிக்கை பதிவு",
        "report": "📄 EHR அறிக்கை",
        "download": "⬇️ EHR அறிக்கையை PDF ஆக பதிவிறக்கவும்",
        "no_data": "இந்த நோயாளிக்கு தகவல் எதுவும் கிடைக்கவில்லை.",
        "patient_id": "நோயாளர் ID",
        "age": "வயது",
        "gender": "பாலினம்",
        "state": "மாநிலம்",
        "insurance": "காப்பீடு",
        "bpl": "BPL அட்டை",
        "admissions": "மொத்த அனுமதிகள்",
        "latest": "சமீபத்திய அனுமதி",
        "avg_los": "சராசரி தங்கிய நாட்கள்",
        "readmissions": "30 நாள் மீண்டும் அனுமதி",
        "total_cost": "மொத்த செலவு",
        "subsidy": "அரசு மானியம்",
        "out_of_pocket": "சுய செலவு",
        "secure": "🔒 இந்த சுகாதார தகவலை அங்கீகரிக்கப்பட்ட பயனர்கள் மட்டுமே பார்க்க முடியும்.",
        "select_patient": "நோயாளியைத் தேர்ந்தெடுக்கவும்",
        "unauthorized": "இந்த EHR-ஐ பார்க்க உங்களுக்கு அனுமதி இல்லை.",
        "risk": "ஆபத்து நிலை",
        "probability": "மீண்டும் அனுமதிக்கப்படும் வாய்ப்பு",
        "summary": "மருத்துவ சுருக்கம்",
        "recommendations": "பரிந்துரைகள்",
        "block": "பிளாக்",
        "record_type": "பதிவு வகை",
        "created_by": "உருவாக்கியவர்",
        "verified": "பிளாக்செயின் ஒருமைப்பாடு வெற்றிகரமாக சரிபார்க்கப்பட்டது.",
        "no_blockchain": "இந்த நோயாளிக்கு பிளாக்செயின் தணிக்கை பதிவு இல்லை.",
        "pdf_title": "CareWatch-AI மின்னணு சுகாதார பதிவு",
        "prepared": "தயாரிக்கப்பட்டது",
        "comorbidity": "இணை நோய் எண்ணிக்கை",
        "previous_admissions": "முந்தைய அனுமதிகள்",
        "hospital_name": "மருத்துவமனை",
        "hospital_tier": "மருத்துவமனை வகை",
        "beds": "படுக்கைகள்",
        "teaching": "கற்பித்தல் மருத்துவமனை"
    },

    "Hindi": {
        "title": "📋 इलेक्ट्रॉनिक स्वास्थ्य रिकॉर्ड",
        "subtitle": "सुरक्षित रोगी स्वास्थ्य रिकॉर्ड",
        "profile": "👤 रोगी प्रोफ़ाइल",
        "history": "🏥 भर्ती इतिहास",
        "diagnosis": "🩺 निदान इतिहास",
        "billing": "💰 बिलिंग इतिहास",
        "hospital": "🏨 अस्पताल की जानकारी",
        "prediction": "🤖 AI पुनः भर्ती जोखिम",
        "blockchain": "🔗 ब्लॉकचेन ऑडिट रिकॉर्ड",
        "report": "📄 EHR रिपोर्ट",
        "download": "⬇️ EHR रिपोर्ट PDF डाउनलोड करें",
        "no_data": "इस रोगी के लिए कोई जानकारी नहीं मिली।",
        "patient_id": "रोगी ID",
        "age": "आयु",
        "gender": "लिंग",
        "state": "राज्य",
        "insurance": "बीमा",
        "bpl": "BPL कार्ड",
        "admissions": "कुल भर्ती",
        "latest": "नवीनतम भर्ती",
        "avg_los": "औसत भर्ती अवधि",
        "readmissions": "30-दिन पुनः भर्ती",
        "total_cost": "कुल लागत",
        "subsidy": "सरकारी सब्सिडी",
        "out_of_pocket": "स्वयं भुगतान",
        "secure": "🔒 यह स्वास्थ्य जानकारी केवल अधिकृत उपयोगकर्ताओं के लिए उपलब्ध है।",
        "select_patient": "रोगी चुनें",
        "unauthorized": "आपको यह EHR देखने की अनुमति नहीं है।",
        "risk": "जोखिम स्तर",
        "probability": "पुनः भर्ती संभावना",
        "summary": "चिकित्सकीय सारांश",
        "recommendations": "सिफारिशें",
        "block": "ब्लॉक",
        "record_type": "रिकॉर्ड प्रकार",
        "created_by": "द्वारा बनाया गया",
        "verified": "ब्लॉकचेन अखंडता सफलतापूर्वक सत्यापित हुई।",
        "no_blockchain": "इस रोगी के लिए कोई ब्लॉकचेन ऑडिट रिकॉर्ड उपलब्ध नहीं है।",
        "pdf_title": "CareWatch-AI इलेक्ट्रॉनिक स्वास्थ्य रिकॉर्ड",
        "prepared": "तैयार किया गया",
        "comorbidity": "सह-रोग संख्या",
        "previous_admissions": "पिछली भर्ती",
        "hospital_name": "अस्पताल",
        "hospital_tier": "अस्पताल स्तर",
        "beds": "बेड",
        "teaching": "शिक्षण अस्पताल"
    },

    "Kannada": {
        "title": "📋 ಎಲೆಕ್ಟ್ರಾನಿಕ್ ಆರೋಗ್ಯ ದಾಖಲೆ",
        "subtitle": "ಸುರಕ್ಷಿತ ರೋಗಿಯ ಆರೋಗ್ಯ ದಾಖಲೆ",
        "profile": "👤 ರೋಗಿಯ ವಿವರಗಳು",
        "history": "🏥 ದಾಖಲಾತಿ ಇತಿಹಾಸ",
        "diagnosis": "🩺 ರೋಗನಿರ್ಣಯ ಇತಿಹಾಸ",
        "billing": "💰 ಬಿಲ್ಲಿಂಗ್ ಇತಿಹಾಸ",
        "hospital": "🏨 ಆಸ್ಪತ್ರೆ ಮಾಹಿತಿ",
        "prediction": "🤖 AI ಮರುದಾಖಲಾತಿ ಅಪಾಯ",
        "blockchain": "🔗 ಬ್ಲಾಕ್‌ಚೈನ್ ಆಡಿಟ್ ದಾಖಲೆ",
        "report": "📄 EHR ವರದಿ",
        "download": "⬇️ EHR ವರದಿಯನ್ನು PDF ಆಗಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
        "no_data": "ಈ ರೋಗಿಗೆ ಯಾವುದೇ ಮಾಹಿತಿ ಕಂಡುಬಂದಿಲ್ಲ.",
        "patient_id": "ರೋಗಿ ID",
        "age": "ವಯಸ್ಸು",
        "gender": "ಲಿಂಗ",
        "state": "ರಾಜ್ಯ",
        "insurance": "ವಿಮೆ",
        "bpl": "BPL ಕಾರ್ಡ್",
        "admissions": "ಒಟ್ಟು ದಾಖಲಾತಿಗಳು",
        "latest": "ಇತ್ತೀಚಿನ ದಾಖಲಾತಿ",
        "avg_los": "ಸರಾಸರಿ ತಂಗುವಿಕೆ",
        "readmissions": "30 ದಿನಗಳ ಮರುದಾಖಲಾತಿ",
        "total_cost": "ಒಟ್ಟು ವೆಚ್ಚ",
        "subsidy": "ಸರ್ಕಾರಿ ಸಹಾಯಧನ",
        "out_of_pocket": "ಸ್ವಂತ ವೆಚ್ಚ",
        "secure": "🔒 ಈ ಆರೋಗ್ಯ ಮಾಹಿತಿಯನ್ನು ಅಧಿಕೃತ ಬಳಕೆದಾರರು ಮಾತ್ರ ನೋಡಬಹುದು.",
        "select_patient": "ರೋಗಿಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "unauthorized": "ಈ EHR ಅನ್ನು ವೀಕ್ಷಿಸಲು ನಿಮಗೆ ಅನುಮತಿ ಇಲ್ಲ.",
        "risk": "ಅಪಾಯ ಮಟ್ಟ",
        "probability": "ಮರುದಾಖಲಾತಿ ಸಾಧ್ಯತೆ",
        "summary": "ವೈದ್ಯಕೀಯ ಸಾರಾಂಶ",
        "recommendations": "ಶಿಫಾರಸುಗಳು",
        "block": "ಬ್ಲಾಕ್",
        "record_type": "ದಾಖಲೆ ಪ್ರಕಾರ",
        "created_by": "ರಚಿಸಿದವರು",
        "verified": "ಬ್ಲಾಕ್‌ಚೈನ್ ಸಮಗ್ರತೆ ಯಶಸ್ವಿಯಾಗಿ ಪರಿಶೀಲಿಸಲಾಗಿದೆ.",
        "no_blockchain": "ಈ ರೋಗಿಗೆ ಬ್ಲಾಕ್‌ಚೈನ್ ಆಡಿಟ್ ದಾಖಲೆ ಲಭ್ಯವಿಲ್ಲ.",
        "pdf_title": "CareWatch-AI ಎಲೆಕ್ಟ್ರಾನಿಕ್ ಆರೋಗ್ಯ ದಾಖಲೆ",
        "prepared": "ತಯಾರಿಸಲಾಗಿದೆ",
        "comorbidity": "ಸಹ-ರೋಗಗಳ ಸಂಖ್ಯೆ",
        "previous_admissions": "ಹಿಂದಿನ ದಾಖಲಾತಿಗಳು",
        "hospital_name": "ಆಸ್ಪತ್ರೆ",
        "hospital_tier": "ಆಸ್ಪತ್ರೆ ಮಟ್ಟ",
        "beds": "ಹಾಸಿಗೆಗಳು",
        "teaching": "ಬೋಧನಾ ಆಸ್ಪತ್ರೆ"
    },

    "Telugu": {
        "title": "📋 ఎలక్ట్రానిక్ హెల్త్ రికార్డ్",
        "subtitle": "సురక్షిత రోగి ఆరోగ్య రికార్డు",
        "profile": "👤 రోగి వివరాలు",
        "history": "🏥 అడ్మిషన్ చరిత్ర",
        "diagnosis": "🩺 నిర్ధారణ చరిత్ర",
        "billing": "💰 బిల్లింగ్ చరిత్ర",
        "hospital": "🏨 ఆసుపత్రి సమాచారం",
        "prediction": "🤖 AI రీ-అడ్మిషన్ ప్రమాదం",
        "blockchain": "🔗 బ్లాక్‌చెయిన్ ఆడిట్ రికార్డు",
        "report": "📄 EHR నివేదిక",
        "download": "⬇️ EHR నివేదికను PDFగా డౌన్‌లోడ్ చేయండి",
        "no_data": "ఈ రోగికి సమాచారం కనుగొనబడలేదు.",
        "patient_id": "రోగి ID",
        "age": "వయస్సు",
        "gender": "లింగం",
        "state": "రాష్ట్రం",
        "insurance": "బీమా",
        "bpl": "BPL కార్డు",
        "admissions": "మొత్తం అడ్మిషన్లు",
        "latest": "తాజా అడ్మిషన్",
        "avg_los": "సగటు ఆసుపత్రి రోజులు",
        "readmissions": "30 రోజుల రీ-అడ్మిషన్లు",
        "total_cost": "మొత్తం ఖర్చు",
        "subsidy": "ప్రభుత్వ సబ్సిడీ",
        "out_of_pocket": "స్వంత ఖర్చు",
        "secure": "🔒 ఈ ఆరోగ్య సమాచారాన్ని అధీకృత వినియోగదారులు మాత్రమే చూడగలరు.",
        "select_patient": "రోగిని ఎంచుకోండి",
        "unauthorized": "ఈ EHRను చూడటానికి మీకు అనుమతి లేదు.",
        "risk": "ప్రమాద స్థాయి",
        "probability": "రీ-అడ్మిషన్ సంభావ్యత",
        "summary": "వైద్య సారాంశం",
        "recommendations": "సిఫార్సులు",
        "block": "బ్లాక్",
        "record_type": "రికార్డు రకం",
        "created_by": "సృష్టించినవారు",
        "verified": "బ్లాక్‌చెయిన్ సమగ్రత విజయవంతంగా ధృవీకరించబడింది.",
        "no_blockchain": "ఈ రోగికి బ్లాక్‌చెయిన్ ఆడిట్ రికార్డు లేదు.",
        "pdf_title": "CareWatch-AI ఎలక్ట్రానిక్ హెల్త్ రికార్డ్",
        "prepared": "తయారు చేయబడింది",
        "comorbidity": "కో-మార్బిడిటీ సంఖ్య",
        "previous_admissions": "మునుపటి అడ్మిషన్లు",
        "hospital_name": "ఆసుపత్రి",
        "hospital_tier": "ఆసుపత్రి స్థాయి",
        "beds": "పడకలు",
        "teaching": "బోధనా ఆసుపత్రి"
    },

    "Malayalam": {
        "title": "📋 ഇലക്ട്രോണിക് ഹെൽത്ത് റെക്കോർഡ്",
        "subtitle": "സുരക്ഷിതമായ രോഗിയുടെ ആരോഗ്യ രേഖ",
        "profile": "👤 രോഗിയുടെ വിവരങ്ങൾ",
        "history": "🏥 പ്രവേശന ചരിത്രം",
        "diagnosis": "🩺 രോഗനിർണയ ചരിത്രം",
        "billing": "💰 ബില്ലിംഗ് ചരിത്രം",
        "hospital": "🏨 ആശുപത്രി വിവരങ്ങൾ",
        "prediction": "🤖 AI വീണ്ടും പ്രവേശന അപകടസാധ്യത",
        "blockchain": "🔗 ബ്ലോക്ക്ചെയിൻ ഓഡിറ്റ് രേഖ",
        "report": "📄 EHR റിപ്പോർട്ട്",
        "download": "⬇️ EHR റിപ്പോർട്ട് PDF ആയി ഡൗൺലോഡ് ചെയ്യുക",
        "no_data": "ഈ രോഗിക്കായി വിവരങ്ങളൊന്നും കണ്ടെത്തിയില്ല.",
        "patient_id": "രോഗി ID",
        "age": "പ്രായം",
        "gender": "ലിംഗം",
        "state": "സംസ്ഥാനം",
        "insurance": "ഇൻഷുറൻസ്",
        "bpl": "BPL കാർഡ്",
        "admissions": "ആകെ പ്രവേശനങ്ങൾ",
        "latest": "ഏറ്റവും പുതിയ പ്രവേശനം",
        "avg_los": "ശരാശരി താമസദിവസങ്ങൾ",
        "readmissions": "30 ദിവസത്തെ വീണ്ടും പ്രവേശനങ്ങൾ",
        "total_cost": "ആകെ ചെലവ്",
        "subsidy": "സർക്കാർ സബ്സിഡി",
        "out_of_pocket": "സ്വന്തം ചെലവ്",
        "secure": "🔒 ഈ ആരോഗ്യ വിവരങ്ങൾ അംഗീകൃത ഉപയോക്താക്കൾക്ക് മാത്രം ലഭ്യമാണ്.",
        "select_patient": "രോഗിയെ തിരഞ്ഞെടുക്കുക",
        "unauthorized": "ഈ EHR കാണാൻ നിങ്ങൾക്ക് അനുമതിയില്ല.",
        "risk": "അപകട നില",
        "probability": "വീണ്ടും പ്രവേശന സാധ്യത",
        "summary": "ക്ലിനിക്കൽ സംഗ്രഹം",
        "recommendations": "ശുപാർശകൾ",
        "block": "ബ്ലോക്ക്",
        "record_type": "റെക്കോർഡ് തരം",
        "created_by": "സൃഷ്ടിച്ചത്",
        "verified": "ബ്ലോക്ക്ചെയിൻ സമഗ്രത വിജയകരമായി പരിശോധിച്ചു.",
        "no_blockchain": "ഈ രോഗിക്ക് ബ്ലോക്ക്ചെയിൻ ഓഡിറ്റ് രേഖ ലഭ്യമല്ല.",
        "pdf_title": "CareWatch-AI ഇലക്ട്രോണിക് ഹെൽത്ത് റെക്കോർഡ്",
        "prepared": "തയ്യാറാക്കിയത്",
        "comorbidity": "സഹരോഗങ്ങളുടെ എണ്ണം",
        "previous_admissions": "മുൻ പ്രവേശനങ്ങൾ",
        "hospital_name": "ആശുപത്രി",
        "hospital_tier": "ആശുപത്രി തരം",
        "beds": "കിടക്കകൾ",
        "teaching": "അധ്യാപന ആശുപത്രി"
    }
}

T = TEXT.get(language, TEXT["English"])


# =========================================================
# LOAD CSV
# =========================================================

@st.cache_data
def load_csv(filename):

    path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


patients = load_csv("patients.csv")
admissions = load_csv("admissions.csv")
diagnoses = load_csv("diagnoses.csv")
billing = load_csv("billing.csv")
hospitals = load_csv("hospitals.csv")


# =========================================================
# NORMALIZE IDs
# =========================================================

for df, column in [
    (patients, "patient_id"),
    (admissions, "patient_id"),
    (admissions, "admission_id"),
    (diagnoses, "admission_id"),
    (billing, "admission_id"),
    (hospitals, "hospital_id")
]:

    if column in df.columns:
        df[column] = df[column].astype(str).str.strip()


# =========================================================
# SELECT PATIENT
# =========================================================

if role == "Patient":

    patient_id = st.session_state.get("patient_id")

    if not patient_id:
        st.error(T["no_data"])
        st.stop()

    patient_id = str(patient_id).strip()

elif role in ["Doctor", "Admin"]:

    if patients.empty:
        st.error(T["no_data"])
        st.stop()

    patient_ids = (
        patients["patient_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    patient_id = st.selectbox(
        T["select_patient"],
        sorted(patient_ids)
    )

else:

    st.error(T["unauthorized"])
    st.stop()


# =========================================================
# PATIENT
# =========================================================

patient_rows = patients[
    patients["patient_id"] == patient_id
]

if patient_rows.empty:
    st.warning(T["no_data"])
    st.stop()

patient = patient_rows.iloc[0]


# =========================================================
# GET ADMISSIONS
# =========================================================

patient_admissions = admissions[
    admissions["patient_id"] == patient_id
].copy() if not admissions.empty else pd.DataFrame()


if not patient_admissions.empty:

    for col in ["admit_date", "discharge_date"]:

        if col in patient_admissions.columns:

            patient_admissions[col] = pd.to_datetime(
                patient_admissions[col],
                errors="coerce"
            )

    if "admit_date" in patient_admissions.columns:

        patient_admissions = patient_admissions.sort_values(
            "admit_date",
            ascending=False
        )


# =========================================================
# GET DIAGNOSES
# =========================================================

patient_diagnoses = pd.DataFrame()

if (
    not patient_admissions.empty
    and not diagnoses.empty
    and "admission_id" in patient_admissions.columns
):

    admission_ids = (
        patient_admissions["admission_id"]
        .astype(str)
        .tolist()
    )

    patient_diagnoses = diagnoses[
        diagnoses["admission_id"].isin(admission_ids)
    ].copy()


# =========================================================
# GET BILLING
# =========================================================

patient_billing = pd.DataFrame()

if (
    not patient_admissions.empty
    and not billing.empty
    and "admission_id" in patient_admissions.columns
):

    admission_ids = (
        patient_admissions["admission_id"]
        .astype(str)
        .tolist()
    )

    patient_billing = billing[
        billing["admission_id"].isin(admission_ids)
    ].copy()


# =========================================================
# GET HOSPITAL
# =========================================================

patient_hospitals = pd.DataFrame()

if (
    not patient_admissions.empty
    and not hospitals.empty
    and "hospital_id" in patient_admissions.columns
):

    hospital_ids = (
        patient_admissions["hospital_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    patient_hospitals = hospitals[
        hospitals["hospital_id"].isin(hospital_ids)
    ].copy()


# =========================================================
# HEADER
# =========================================================

st.title(T["title"])
st.caption(T["subtitle"])

st.markdown("---")


# =========================================================
# PROFILE
# =========================================================

st.header(T["profile"])

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(T["patient_id"], patient_id)

with c2:
    st.metric(T["age"], str(patient.get("age", "N/A")))

with c3:
    st.metric(T["gender"], str(patient.get("gender", "N/A")))

with c4:
    st.metric(T["state"], str(patient.get("state", "N/A")))


c1, c2, c3 = st.columns(3)

with c1:
    st.info(
        f"**{T['insurance']}:** "
        f"{patient.get('insurance_type', 'N/A')}"
    )

with c2:
    st.info(
        f"**{T['bpl']}:** "
        f"{patient.get('bpl_card', 'N/A')}"
    )

with c3:
    st.info(
        f"**{T['comorbidity']}:** "
        f"{patient.get('comorbidity_count', 'N/A')}"
    )


# =========================================================
# ADMISSION HISTORY
# =========================================================

st.markdown("---")
st.header(T["history"])

if patient_admissions.empty:

    st.info(T["no_data"])

else:

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            T["admissions"],
            len(patient_admissions)
        )

    with c2:

        latest = "N/A"

        if "admit_date" in patient_admissions.columns:

            valid = patient_admissions["admit_date"].dropna()

            if not valid.empty:
                latest = valid.iloc[0].strftime("%Y-%m-%d")

        st.metric(T["latest"], latest)

    with c3:

        avg_los = pd.to_numeric(
            patient_admissions.get("los_days", pd.Series(dtype=float)),
            errors="coerce"
        ).mean()

        st.metric(
            T["avg_los"],
            f"{avg_los:.1f} days"
            if pd.notna(avg_los)
            else "N/A"
        )

    with c4:

        if "readmitted_30d" in patient_admissions.columns:

            readmitted = (
                patient_admissions["readmitted_30d"]
                .astype(str)
                .str.lower()
                .isin(["1", "true", "yes"])
                .sum()
            )

            st.metric(
                T["readmissions"],
                int(readmitted)
            )

    display_columns = [
        "admission_id",
        "admit_date",
        "discharge_date",
        "los_days",
        "admit_type",
        "ward_type",
        "discharge_type",
        "num_procedures",
        "charlson_index",
        "hba1c",
        "creatinine",
        "haemoglobin",
        "systolic_bp",
        "readmitted_30d"
    ]

    display_columns = [
        c for c in display_columns
        if c in patient_admissions.columns
    ]

    display = patient_admissions[display_columns].copy()

    for col in ["admit_date", "discharge_date"]:

        if col in display.columns:

            display[col] = display[col].dt.strftime("%Y-%m-%d")

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# DIAGNOSIS
# =========================================================

st.markdown("---")
st.header(T["diagnosis"])

if patient_diagnoses.empty:

    st.info(T["no_data"])

else:

    diagnosis_columns = [
        "admission_id",
        "icd10_code",
        "diag_desc",
        "diag_rank",
        "diag_category"
    ]

    diagnosis_columns = [
        c for c in diagnosis_columns
        if c in patient_diagnoses.columns
    ]

    st.dataframe(
        patient_diagnoses[diagnosis_columns],
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# BILLING
# =========================================================

st.markdown("---")
st.header(T["billing"])

if patient_billing.empty:

    st.info(T["no_data"])

else:

    for col in [
        "total_cost_inr",
        "govt_subsidy_inr",
        "out_of_pocket_inr"
    ]:

        if col in patient_billing.columns:

            patient_billing[col] = pd.to_numeric(
                patient_billing[col],
                errors="coerce"
            )

    total = (
        patient_billing["total_cost_inr"].sum()
        if "total_cost_inr" in patient_billing
        else 0
    )

    subsidy = (
        patient_billing["govt_subsidy_inr"].sum()
        if "govt_subsidy_inr" in patient_billing
        else 0
    )

    oop = (
        patient_billing["out_of_pocket_inr"].sum()
        if "out_of_pocket_inr" in patient_billing
        else 0
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            T["total_cost"],
            f"₹{total:,.2f}"
        )

    with c2:
        st.metric(
            T["subsidy"],
            f"₹{subsidy:,.2f}"
        )

    with c3:
        st.metric(
            T["out_of_pocket"],
            f"₹{oop:,.2f}"
        )

    st.dataframe(
        patient_billing,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# HOSPITAL
# =========================================================

st.markdown("---")
st.header(T["hospital"])

if patient_hospitals.empty:

    st.info(T["no_data"])

else:

    st.dataframe(
        patient_hospitals,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# AI PREDICTION DATA
# =========================================================

st.markdown("---")
st.header(T["prediction"])

prediction_file = os.path.join(
    BASE_DIR,
    "prediction_results.csv"
)

prediction_rows = pd.DataFrame()

if os.path.exists(prediction_file):

    try:

        prediction_df = pd.read_csv(
            prediction_file
        )

        if "patient_id" in prediction_df.columns:

            prediction_df["patient_id"] = (
                prediction_df["patient_id"]
                .astype(str)
                .str.strip()
            )

            prediction_rows = prediction_df[
                prediction_df["patient_id"] == patient_id
            ].copy()

    except Exception:
        prediction_rows = pd.DataFrame()


latest_prediction = None

if not prediction_rows.empty:

    latest_prediction = prediction_rows.iloc[-1]

    risk = latest_prediction.get(
        "risk_level",
        latest_prediction.get("Risk Level", "N/A")
    )

    probability = latest_prediction.get(
        "probability",
        latest_prediction.get(
            "readmission_probability",
            latest_prediction.get(
                "Readmission Probability",
                None
            )
        )
    )

    st.metric(
        T["risk"],
        str(risk)
    )

    if probability is not None:

        try:

            probability_value = float(probability)

            if probability_value <= 1:
                probability_value *= 100

            st.metric(
                T["probability"],
                f"{probability_value:.2f}%"
            )

        except Exception:
            st.write(
                f"**{T['probability']}:** {probability}"
            )

    summary = latest_prediction.get(
        "clinical_summary",
        latest_prediction.get(
            "summary",
            "AI prediction available."
        )
    )

    st.subheader(T["summary"])
    st.write(summary)

    recommendations = latest_prediction.get(
        "recommendations",
        ""
    )

    if recommendations:

        st.subheader(T["recommendations"])

        for item in str(recommendations).split("|"):

            if item.strip():
                st.write(f"✅ {item.strip()}")

else:

    st.info(
        "No AI prediction is currently available for this patient."
        if language == "English"
        else T["no_data"]
    )


# =========================================================
# BLOCKCHAIN
# =========================================================

st.markdown("---")
st.header(T["blockchain"])

blockchain_file = os.path.join(
    BASE_DIR,
    "blockchain.json"
)

blockchain_records = []

if os.path.exists(blockchain_file):

    try:

        import json

        with open(
            blockchain_file,
            "r",
            encoding="utf-8"
        ) as f:

            blockchain_records = json.load(f)

    except Exception:

        blockchain_records = []


patient_blocks = []

if isinstance(blockchain_records, list):

    for block in blockchain_records:

        if not isinstance(block, dict):
            continue

        if str(block.get("patient_id", "")).strip() == patient_id:

            patient_blocks.append(block)

if patient_blocks:

    latest_block = patient_blocks[-1]

    st.success(T["verified"])

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            T["block"],
            str(latest_block.get("block_index", "N/A"))
        )

    with c2:
        st.metric(
            T["record_type"],
            str(latest_block.get("record_type", "N/A"))
        )

    with c3:
        st.metric(
            T["created_by"],
            str(latest_block.get("created_by", "N/A"))
        )

    st.code(
        str(latest_block.get("hash", "")),
        language="text"
    )

else:

    st.info(T["no_blockchain"])


# =========================================================
# PDF GENERATION
# =========================================================

def generate_pdf():

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading = styles["Heading2"]
    normal = styles["BodyText"]

    story = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            T["pdf_title"],
            title_style
        )
    )

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            f"{T['prepared']}: "
            f"{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            normal
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # -----------------------------------------------------
    # PROFILE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            T["profile"],
            heading
        )
    )

    profile_data = [
        [T["patient_id"], patient_id],
        [T["age"], str(patient.get("age", "N/A"))],
        [T["gender"], str(patient.get("gender", "N/A"))],
        [T["state"], str(patient.get("state", "N/A"))],
        [
            T["insurance"],
            str(patient.get("insurance_type", "N/A"))
        ],
        [
            T["bpl"],
            str(patient.get("bpl_card", "N/A"))
        ],
        [
            T["comorbidity"],
            str(patient.get("comorbidity_count", "N/A"))
        ],
        [
            T["previous_admissions"],
            str(patient.get("prev_admissions", "N/A"))
        ]
    ]

    table = Table(
        profile_data,
        colWidths=[170, 300]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9)
        ])
    )

    story.append(table)
    story.append(Spacer(1, 15))

    # -----------------------------------------------------
    # ADMISSIONS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            T["history"],
            heading
        )
    )

    if not patient_admissions.empty:

        admission_pdf = patient_admissions.copy()

        for col in [
            "admit_date",
            "discharge_date"
        ]:

            if col in admission_pdf.columns:

                admission_pdf[col] = (
                    admission_pdf[col]
                    .dt.strftime("%Y-%m-%d")
                )

        columns = [
            "admission_id",
            "admit_date",
            "discharge_date",
            "los_days",
            "admit_type",
            "ward_type",
            "discharge_type"
        ]

        columns = [
            c for c in columns
            if c in admission_pdf.columns
        ]

        data = [columns]

        for _, row in admission_pdf[columns].iterrows():

            data.append(
                [
                    str(row[c])
                    for c in columns
                ]
            )

        table = Table(
            data,
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP")
            ])
        )

        story.append(table)

    else:

        story.append(
            Paragraph(
                T["no_data"],
                normal
            )
        )

    story.append(Spacer(1, 15))

    # -----------------------------------------------------
    # DIAGNOSIS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            T["diagnosis"],
            heading
        )
    )

    if not patient_diagnoses.empty:

        columns = [
            "icd10_code",
            "diag_desc",
            "diag_category"
        ]

        columns = [
            c for c in columns
            if c in patient_diagnoses.columns
        ]

        data = [columns]

        for _, row in patient_diagnoses[columns].iterrows():

            data.append(
                [
                    str(row[c])
                    for c in columns
                ]
            )

        table = Table(
            data,
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 7)
            ])
        )

        story.append(table)

    else:

        story.append(
            Paragraph(
                T["no_data"],
                normal
            )
        )

    story.append(Spacer(1, 15))

    # -----------------------------------------------------
    # BILLING
    # -----------------------------------------------------

    story.append(
        Paragraph(
            T["billing"],
            heading
        )
    )

    if not patient_billing.empty:

        total = (
            patient_billing["total_cost_inr"].sum()
            if "total_cost_inr" in patient_billing
            else 0
        )

        subsidy = (
            patient_billing["govt_subsidy_inr"].sum()
            if "govt_subsidy_inr" in patient_billing
            else 0
        )

        oop = (
            patient_billing["out_of_pocket_inr"].sum()
            if "out_of_pocket_inr" in patient_billing
            else 0
        )

        billing_data = [
            [T["total_cost"], f"₹{total:,.2f}"],
            [T["subsidy"], f"₹{subsidy:,.2f}"],
            [T["out_of_pocket"], f"₹{oop:,.2f}"]
        ]

        table = Table(
            billing_data,
            colWidths=[250, 200]
        )

        table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 9)
            ])
        )

        story.append(table)

    story.append(Spacer(1, 15))

    # -----------------------------------------------------
    # AI PREDICTION
    # -----------------------------------------------------

    story.append(
        Paragraph(
            T["prediction"],
            heading
        )
    )

    if latest_prediction is not None:

        risk = latest_prediction.get(
            "risk_level",
            latest_prediction.get(
                "Risk Level",
                "N/A"
            )
        )

        probability = latest_prediction.get(
            "probability",
            latest_prediction.get(
                "readmission_probability",
                latest_prediction.get(
                    "Readmission Probability",
                    "N/A"
                )
            )
        )

        prediction_data = [
            [T["risk"], str(risk)],
            [T["probability"], str(probability)]
        ]

        table = Table(
            prediction_data,
            colWidths=[250, 200]
        )

        table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 9)
            ])
        )

        story.append(table)

        story.append(Spacer(1, 10))

        summary = latest_prediction.get(
            "clinical_summary",
            latest_prediction.get(
                "summary",
                ""
            )
        )

        if summary:

            story.append(
                Paragraph(
                    f"<b>{T['summary']}:</b> "
                    f"{str(summary)}",
                    normal
                )
            )

    # -----------------------------------------------------
    # BLOCKCHAIN
    # -----------------------------------------------------

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            T["blockchain"],
            heading
        )
    )

    if patient_blocks:

        block = patient_blocks[-1]

        blockchain_data = [
            [
                T["block"],
                str(block.get("block_index", "N/A"))
            ],
            [
                T["record_type"],
                str(block.get("record_type", "N/A"))
            ],
            [
                T["created_by"],
                str(block.get("created_by", "N/A"))
            ],
            [
                "Hash",
                str(block.get("hash", "N/A"))
            ]
        ]

        table = Table(
            blockchain_data,
            colWidths=[170, 300]
        )

        table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP")
            ])
        )

        story.append(table)

    else:

        story.append(
            Paragraph(
                T["no_blockchain"],
                normal
            )
        )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            T["secure"],
            normal
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# DOWNLOAD PDF
# =========================================================

st.markdown("---")

st.header(T["report"])

try:

    pdf_bytes = generate_pdf()

    st.download_button(
        label=T["download"],
        data=pdf_bytes,
        file_name=f"CareWatch_EHR_{patient_id}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.success(
        "PDF report is ready."
        if language == "English"
        else "PDF அறிக்கை தயாராக உள்ளது."
        if language == "Tamil"
        else "PDF रिपोर्ट तैयार है."
        if language == "Hindi"
        else "PDF ವರದಿ ಸಿದ್ಧವಾಗಿದೆ."
        if language == "Kannada"
        else "PDF నివేదిక సిద్ధంగా ఉంది."
        if language == "Telugu"
        else "PDF റിപ്പോർട്ട് തയ്യാറാണ്."
    )

except Exception as e:

    st.error(
        f"Unable to generate PDF report: {e}"
    )


# =========================================================
# SECURITY
# =========================================================

st.markdown("---")

st.info(T["secure"])

st.caption(
    f"CareWatch-AI | Role: {role}"
)