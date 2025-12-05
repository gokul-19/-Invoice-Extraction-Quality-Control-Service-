import streamlit as st
import json
from invoice_qc.extractor import InvoiceExtractor
from invoice_qc.validator import InvoiceValidator

st.set_page_config(page_title="Invoice QC Service", layout="wide")

# --- HEADER ---
st.title("📄 Invoice Quality Control Service")
st.write("Upload PDF invoices → extract → validate → get summary report")

uploaded_file = st.file_uploader("Upload a PDF Invoice", type=["pdf"])

if uploaded_file:
    st.success("PDF uploaded successfully!")

    # --- Extraction ---
    st.header("🔍 Extraction Results")

    loader = InvoiceLoader()

    try:
        extracted = loader.load_pdf(uploaded_file)

        st.json(extracted)

    except Exception as e:
        st.error(f"Extraction failed: {e}")
        st.stop()

    st.divider()

    # --- VALIDATION ---
    st.header("📌 Validation Results")

    validator = InvoiceValidator()
    qc_report = validator.validate([extracted])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Invoice Validation")
        st.json(qc_report["results"])

    with col2:
        st.subheader("Summary")
        st.json(qc_report["summary"])

    st.divider()

    # --- DOWNLOAD REPORT ---
    st.header("⬇️ Download QC Report")

    report_json = json.dumps(qc_report, indent=4)

    st.download_button(
        label="Download JSON Report",
        data=report_json,
        file_name="invoice_qc_report.json",
        mime="application/json",
    )
