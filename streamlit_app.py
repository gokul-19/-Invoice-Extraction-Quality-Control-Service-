import streamlit as st
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from invoice_qc.extractor import InvoiceExtractor
from invoice_qc.validator import InvoiceValidator

st.set_page_config(page_title="Invoice QC Service", layout="wide")

st.title("📄 Invoice Quality Control Service")
st.write("Upload PDF invoices → extract → validate → download report")

uploaded_files = st.file_uploader(
    "Upload one or more PDF invoices",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")

    extractor = InvoiceExtractor()
    validator = InvoiceValidator()

    invoices = []

    st.header("🔍 Extraction Results")
    for file in uploaded_files:
        try:
            extracted_invoice = extractor.extract_single(file)
            invoices.append(extracted_invoice.dict())
            st.subheader(f"Invoice: {extracted_invoice.invoice_number}")
            st.json(extracted_invoice.dict())
        except Exception as e:
            st.error(f"Extraction failed for {file.name}: {e}")

    if invoices:
        st.divider()
        st.header("📌 Validation Results")

        qc_report = validator.validate(invoices)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Per-Invoice Validation")
            st.json(qc_report["results"])

        with col2:
            st.subheader("Summary")
            st.json(qc_report["summary"])

        st.divider()
        st.header("⬇️ Download QC Report")

        report_json = json.dumps(qc_report, indent=4)
        st.download_button(
            label="Download JSON Report",
            data=report_json,
            file_name="invoice_qc_report.json",
            mime="application/json"
        )
