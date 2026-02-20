import streamlit as st
import requests
import json
import base64

API_URL = "http://127.0.0.1:8000/analyze"

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

uploaded_file = st.file_uploader("Upload VCF File (optional - uses default database if not provided)", type=["vcf"])

if st.button("Analyze"):

    # File upload is now optional - uses default database if not provided
    if uploaded_file:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")
        }
    else:
        files = None

    with st.spinner("Analyzing genetic profile..."):
        response = requests.post(API_URL, files=files, params={"drug": drug})

    data = response.json()
    result = data.get("result", {})
    recommendation = result.get("recommendation", "Unknown")
    confidence = result.get("confidence", 0)
    # Ensure confidence is between 0 and 1 for the progress bar
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
