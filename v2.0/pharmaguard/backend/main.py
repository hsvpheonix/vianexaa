from fastapi import FastAPI, UploadFile
import shutil
import os
import sys
import uuid

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from parser import parse_vcf
from rules_engine import evaluate
from llm import generate_explanation
from pdf_report import generate_pdf

app = FastAPI()

from fastapi.responses import JSONResponse
import base64

# Get the directory of this file to find sample VCF files
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_VCF_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "sample_vcf")

# Full pharmacogenomics database - contains all genes (DPYD, TPMT, CYP2C19, CYP2C9, SLCO1B1, CYP2D6)
FULL_PGX_VCF = os.path.join(SAMPLE_VCF_DIR, "patient_full_pharmacogenomics.vcf")

# Default VCF files for each drug
DEFAULT_VCF_FILES = {
    "Codeine": os.path.join(SAMPLE_VCF_DIR, "patient_codeine_poor.vcf"),
    "Warfarin": os.path.join(SAMPLE_VCF_DIR, "patient_warfarin_adjust.vcf"),
    "Simvastatin": os.path.join(SAMPLE_VCF_DIR, "patient_simvastatin_toxic.vcf"),
    "Clopidogrel": FULL_PGX_VCF,  # Uses CYP2C19 gene
    "Azathioprine": FULL_PGX_VCF,  # Uses TPMT gene
    "Fluorouracil": FULL_PGX_VCF,  # Uses DPYD gene
}

@app.post("/analyze")
async def analyze(drug: str, file: UploadFile = None):

    # Determine which VCF file to use
    if file and file.filename:
        # User uploaded a file
        temp_vcf_path = f"temp_{uuid.uuid4().hex}.vcf"
        with open(temp_vcf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        vcf_path = temp_vcf_path
        temp_file_created = True
    else:
        # Use default VCF file based on drug
        if drug in DEFAULT_VCF_FILES and os.path.exists(DEFAULT_VCF_FILES[drug]):
            vcf_path = DEFAULT_VCF_FILES[drug]
            temp_file_created = False
        else:
            # No file provided and no default available
            return {
                "drug": drug,
                "result": {
                    "recommendation": "Please upload a VCF file",
                    "confidence": 0
                },
                "confidence": 0,
                "explanation": "No VCF file provided. Please upload a VCF file for analysis.",
                "pdf_base64": "",
            }

    variants = parse_vcf(vcf_path)
    result = evaluate(drug, variants)

    explanation = None
    if result.get("gene"):
        explanation = generate_explanation(
            drug,
            result.get("gene"),
            result.get("phenotype"),
        )

    # Generate PDF
    pdf_filename = f"report_{uuid.uuid4().hex}.pdf"
    generate_pdf(
        {
            "drug": drug,
            "result": result,
            "explanation": explanation,
        },
        file_path=pdf_filename,
    )

    # Read PDF as bytes
    with open(pdf_filename, "rb") as f:
        pdf_bytes = f.read()

    # Encode to base64 so JSON can carry it
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    # Cleanup temp files
    if temp_file_created and os.path.exists(vcf_path):
        os.remove(vcf_path)
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

    return {
        "drug": drug,
        "result": result,
        "confidence": result.get("confidence", 0),
        "explanation": explanation,
        "pdf_base64": encoded_pdf,
    }
