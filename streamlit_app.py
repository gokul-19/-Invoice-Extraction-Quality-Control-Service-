import streamlit as st
import sys, os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

st.title("Invoice QC Dashboard")

st.write("Backend health check:")

try:
    from invoice_qc.api import app  # or whatever check you want
    st.success("Backend module loaded")
except Exception as e:
    st.error("Failed to load backend module")
    st.exception(e)
