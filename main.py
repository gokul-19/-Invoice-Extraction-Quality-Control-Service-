from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from invoice_qc.extractor import InvoiceExtractor
from invoice_qc.validator import InvoiceValidator

import tempfile
import shutil
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

extractor = InvoiceExtractor()
validator = InvoiceValidator()


@app.get("/", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
async def upload_and_validate(request: Request, file: UploadFile = File(...)):

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_invoice = extractor.extract_from_file(temp_path)
    validation_result = validator.validate([extracted_invoice])

    os.remove(temp_path)
    os.rmdir(temp_dir)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "invoice": extracted_invoice,
            "result": validation_result,
        }
    )
