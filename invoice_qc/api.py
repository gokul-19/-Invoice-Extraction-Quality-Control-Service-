from fastapi import FastAPI
from typing import List
from .schemas import Invoice
from .validator import InvoiceValidator

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/validate-json")
def validate_json(invoices: List[Invoice]):
    validator = InvoiceValidator()
    return validator.validate(invoices)

