import streamlit as st
import json

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

# Demo results for sample files
DEMO_RESULTS = {
    "Codeine - Normal Metabolizer": {
        "gene": "CYP2D6",
        "phenotype": "Normal Metabolizer (*1/*1)",
        "recommendation": "Use label-recommended dosage",
        "confidence": 0.95,
        "explanation": "The patient has normal CYP2D6 enzyme activity (normal metabolizer). Standard codeine dosing is appropriate. The patient can convert codeine to morphine normally for effective pain relief."
    },
    "Codeine - Poor Metabolizer": {
        "gene": "CYP2D6",
        "phenotype": "Poor Metabolizer (*4/*4)",
        "recommendation": "Avoid codeine - use alternative analgesic",
        "confidence": 0.98,
        "explanation": "The patient is a CYP2D6 poor metabolizer. They cannot convert codeine to morphine effectively, resulting in inadequate pain relief. Additionally, there is risk of unpredictable response. Recommend using an alternative analgesic such as morphine or non-opioid options."
    },
    "Warfarin - Adjust Dose": {
        "gene": "CYP2C9",
        "phenotype": "Intermediate Metabolizer (*2/*3)",
        "recommendation": "Reduce dose by 25-50% and monitor INR closely",
        "confidence": 0.92,
        "explanation": "The patient has reduced CYP2C9 enzyme activity leading to slower warfarin metabolism. Reduced dosing and careful INR monitoring is required to avoid bleeding complications."
    },
    "Simvastatin - Toxic Response": {
        "gene": "SLCO1B1",
        "phenotype": "High Risk (*5/*5)",
        "recommendation": "Avoid simvastatin - use alternative statin",
        "confidence": 0.96,
        "explanation": "The patient has reduced SLCO1B1 transporter function leading to increased simvastatin levels and high risk of myopathy/rhabdomyolysis. Recommend using an alternative statin (e.g., atorvastatin, rosuvastatin) at a low dose."
    },
    "Full Pharmacogenomics": {
        "gene": "Multiple",
        "phenotype": "Variable",
        "recommendation": "Review individual gene results",
        "confidence": 0.85,
        "explanation": "Full pharmacogenomics panel shows multiple variants. Review each gene-drug interaction individually for personalized dosing recommendations."
    },
    "TC_P1_PATIENT_001_NORMAL": {
        "gene": "CYP2D6",
        "phenotype": "Normal Metabolizer (*1/*1)",
        "recommendation": "Use label-recommended dosage",
        "confidence": 0.95,
        "explanation": "The patient has normal CYP2D6 enzyme activity (normal metabolizer). Standard codeine dosing is appropriate. The patient can convert codeine to morphine normally for effective pain relief."
    },
    "TC_P1_PATIENT_001_Normal (Original)": {
        "gene": "Multiple",
        "phenotype": "Normal for most genes",
        "recommendation": "Use standard dosing for most drugs",
        "confidence": 0.80,
        "explanation": "The patient shows normal metabolizer status for most tested genes including CYP2D6, CYP2C19, CYP2C9, DPYD, TPMT, and SLCO1B1. Standard dosing should be appropriate for most medications."
    }
}

# Sample VCF files
SAMPLE_FILES = list(DEMO_RESULTS.keys())

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

selected_sample = st.selectbox("Select Patient Sample", SAMPLE_FILES)

if st.button("Analyze"):
    result = DEMO_RESULTS[selected_sample]
    recommendation = result["recommendation"]
    confidence = result["confidence"]

    st.markdown("---")

    # Risk Card
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if "Avoid" in recommendation:
        st.markdown(f'<div class="risk-red">🔴 {recommendation}</div>', unsafe_allow_html=True)
    elif "Reduce" in recommendation or "Adjust" in recommendation:
        st.markdown(f'<div class="risk-yellow">🟡 {recommendation}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="risk-green">🟢 {recommendation}</div>', unsafe_allow_html=True)

    st.progress(confidence)
    st.write(f"Confidence Score: {int(confidence*100)}%")

    st.markdown('</div>', unsafe_allow_html=True)

    # Genetic Findings
    st.markdown("### 🧬 Genetic Findings")
    st.write(f"**Gene:** {result['gene']}")
    st.write(f"**Phenotype:** {result['phenotype']}")

    # Drug Information
    if drug in DRUG_INFO:
        st.markdown("### 💊 Drug Information")
        info = DRUG_INFO[drug]
        st.write(f"**Description:** {info['description']}")
        st.write(f"**Mechanism:** {info['mechanism']}")
        st.write(f"**Warnings:** {info['warnings']}")
        st.write(f"**Typical Dose:** {info['typical_dose']}")

    # Explanation
    st.markdown("### 📘 Clinical Explanation")
    st.write(result['explanation'])

    st.markdown("---")

    # Create downloadable report
    report_data = {
        "drug": drug,
        "sample": selected_sample,
        "result": result
    }
    
    st.download_button(
        "Download JSON Report",
        data=json.dumps(report_data, indent=2),
        file_name="vianexa_report.json",
        mime="application/json"
    )
