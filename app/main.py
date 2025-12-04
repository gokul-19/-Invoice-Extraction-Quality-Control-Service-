from fastapi import FastAPI
from invoice_qc.api import app as invoice_app

app = FastAPI()
app.mount("/", invoice_app)
