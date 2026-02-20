import streamlit as st
import requests
import json
import base64
import os

# For local development, use localhost. For deployment, use environment variable
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000/analyze")

# Drug information database
DRUG_INFO = {
    "Codeine": {
        "description": "Opioid pain medication used to treat mild to moderate pain.",
        "mechanism": "Converted to morphine by CYP2D6 enzyme for pain relief.",
        "warnings": "Poor metabolizers may experience toxic morphine levels or ineffective pain relief.",
        "typical_dose": "15-60mg every 4-6 hours as needed",
    },
    "Warfarin": {
        "description": "Anticoagulant (blood thinner) used to prevent blood clots.",
        "mechanism": "Inhibits vitamin K-dependent clotting factors in the liver.",
        "warnings": "Narrow therapeutic window - requires regular INR monitoring.",
        "typical_dose": "2-10mg once daily (individualized)",
    },
    "Simvastatin": {
        "description": "Statin medication used to lower cholesterol.",
        "mechanism": "Inhibits HMG-CoA reductase to reduce cholesterol production.",
        "warnings": "Risk of muscle toxicity (rhabdomyolysis) especially with high doses.",
        "typical_dose": "20-40mg once daily at bedtime",
    },
    "Clopidogrel": {
        "description": "Antiplatelet medication used to prevent blood clots.",
        "mechanism": "Inhibits platelet activation and aggregation.",
        "warnings": "Poor metabolizers may have reduced antiplatelet effect.",
        "typical_dose": "75mg once daily",
    },
    "Azathioprine": {
        "description": "Immunosuppressant used for autoimmune diseases and organ transplantation.",
        "mechanism": "Interferes with DNA synthesis in immune cells.",
        "warnings": "Risk of severe myelosuppression in poor metabolizers.",
        "typical_dose": "1-2mg/kg/day (individualized)",
    },
    "Fluorouracil": {
        "description": "Chemotherapy medication used to treat various cancers.",
        "mechanism": "Inhibits DNA and RNA synthesis in rapidly dividing cells.",
        "warnings": "Risk of severe, potentially fatal toxicity in DPYD deficient patients.",
        "typical_dose": "Various regimens (cycle-dependent)",
    }
}

# Sample VCF files bundled with the app
SAMPLE_FILES = {
    "Codeine - Normal Metabolizer": "sample_vcf/patient_codeine_normal.vcf",
    "Codeine - Poor Metabolizer": "sample_vcf/patient_codeine_poor.vcf",
    "Warfarin - Adjust Dose": "sample_vcf/patient_warfarin_adjust.vcf",
    "Simvastatin - Toxic Response": "sample_vcf/patient_simvastatin_toxic.vcf",
    "Full Pharmacogenomics": "sample_vcf/patient_full_pharmacogenomics.vcf",
    "TC_P1_PATIENT_001_NORMAL": "sample_vcf/TC_P1_PATIENT_001_NORMAL.vcf",
    "TC_P1_PATIENT_001_Normal (Original)": "sample_vcf/TC_P1_PATIENT_001_Normal (1).vcf",
}

st.set_page_config(page_title="Vianexa", layout="centered")

st.markdown("""
<style>
.big-title {
    font-size: 34px;
    font-weight: 700;
}
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #f8f9fa;
    margin-bottom: 20px;
}
.risk-red {color: #d9534f; font-weight: 600;}
.risk-yellow {color: #f0ad4e; font-weight: 600;}
.risk-green {color: #5cb85c; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🧬 Vianexa</div>', unsafe_allow_html=True)
st.caption("AI-Powered Precision Medicine Risk Analyzer")

drug = st.selectbox(
    "Select Drug",
    ["Codeine", "Warfarin", "Simvastatin",
     "Clopidogrel", "Azathioprine", "Fluorouracil"]
)

# Option to use sample file or upload
file_option = st.radio("Choose VCF File Source", ["Use Sample File", "Upload Your Own VCF"])

uploaded_file = None
selected_sample = None

if file_option == "Use Sample File":
    selected_sample = st.selectbox("Select Sample", list(SAMPLE_FILES.keys()))
else:
    uploaded_file = st.file_uploader("Upload VCF File", type=["vcf"])

if st.button("Analyze"):
    files = None
    
    if selected_sample:
        # Read sample file
        sample_path = SAMPLE_FILES[selected_sample]
        if os.path.exists(sample_path):
            with open(sample_path, 'rb') as f:
                files = {"file": (sample_path, f.read(), "text/plain")}
        else:
            st.error(f"Sample file not found: {sample_path}")
            st.stop()
    elif uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
    else:
        st.error("Please select a sample file or upload a VCF file")
        st.stop()

    with st.spinner("Analyzing genetic profile..."):
        try:
            response = requests.post(API_URL, files=files, params={"drug": drug}, timeout=60)
            data = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {e}")
            st.info("Note: This demo requires the backend API to be running. For Streamlit Cloud deployment, the backend would need to be deployed separately on Render.com or similar service.")
            st.stop()

    result = data.get("result", {})
    recommendation = result.get("recommendation", "Unknown")
    confidence = result.get("confidence", 0)
    confidence = min(max(float(confidence), 0.0), 1.0)

    st.markdown("---")

    # Risk Card
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if "Safe" in recommendation:
        st.markdown(f'<div class="risk-green">🟢 {recommendation}</div>', unsafe_allow_html=True)
    elif "Reduce" in recommendation or "Adjust" in recommendation:
        st.markdown(f'<div class="risk-yellow">🟡 {recommendation}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="risk-red">🔴 {recommendation}</div>', unsafe_allow_html=True)

    st.progress(confidence)
    st.write(f"Confidence Score: {int(confidence*100)}%")

    st.markdown('</div>', unsafe_allow_html=True)

    # Genetic Findings
    if result.get("gene"):
        st.markdown("### 🧬 Genetic Findings")
        st.write(f"**Gene:** {result.get('gene')}")
        st.write(f"**Phenotype:** {result.get('phenotype')}")

    # Drug Information
    if drug in DRUG_INFO:
        st.markdown("### 💊 Drug Information")
        info = DRUG_INFO[drug]
        st.write(f"**Description:** {info['description']}")
        st.write(f"**Mechanism:** {info['mechanism']}")
        st.write(f"**Warnings:** {info['warnings']}")
        st.write(f"**Typical Dose:** {info['typical_dose']}")

    # Explanation
    if data.get("explanation"):
        st.markdown("### 📘 Clinical Explanation")
        st.write(data["explanation"])

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download JSON Report",
            data=json.dumps(data, indent=2),
            file_name="pharmaguard_result.json",
            mime="application/json"
        )

    with col2:
        if data.get("pdf_base64"):
            pdf_bytes = base64.b64decode(data["pdf_base64"])
            st.download_button(
                "Download Clinical PDF",
                data=pdf_bytes,
                file_name="pharmaguard_report.pdf",
                mime="application/pdf"
            )
