import pdfplumber
import re
import os
import json
from .schemas import Invoice, LineItem
from .utils import extract_date, extract_amount


class InvoiceExtractor:

    def extract_invoices(self, pdf_dir: str):
        invoices = []
        for filename in os.listdir(pdf_dir):
            if filename.lower().endswith(".pdf"):
                full_path = os.path.join(pdf_dir, filename)
                invoices.append(self.extract_single(full_path))
        return invoices

    def extract_single(self, pdf_path: str):
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        invoice_number = self.extract_invoice_number(full_text)
        invoice_date = extract_date(full_text)
        due_date = self.extract_due_date(full_text)

        seller_name = self.find_after(full_text, "Seller")
        buyer_name = self.find_after(full_text, "Buyer")

        currency = self.extract_currency(full_text)
        net_total = self.extract_amount_near(full_text, "Net")
        tax_amount = self.extract_amount_near(full_text, "Tax")
        gross_total = self.extract_amount_near(full_text, "Total")

        line_items = self.extract_line_items(full_text)

        return Invoice(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            seller_name=seller_name,
            buyer_name=buyer_name,
            currency=currency,
            net_total=net_total,
            tax_amount=tax_amount,
            gross_total=gross_total,
            line_items=line_items,
        )

    # ============= Helpers ==================
    
    def extract_invoice_number(self, text):
        patterns = [
            r"Invoice\s*(No|Number|#)[:\s]+(\S+)",
            r"Invoice\s*ID[:\s]+(\S+)"
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(2) if match.lastindex >= 2 else match.group(1)
        return None

    def extract_due_date(self, text):
        m = re.search(r"Due\s*Date[:\s]+(\d{2}/\d{2}/\d{4})", text)
        return m.group(1) if m else None

    def extract_currency(self, text):
        for cur in ["INR", "EUR", "USD"]:
            if cur in text:
                return cur
        return None

    def extract_amount_near(self, text, label):
        pattern = fr"{label}[:\s]+(\d+[\.,]?\d*)"
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return float(m.group(1).replace(",", ""))
        return None

    def extract_line_items(self, text):
        items = []
        lines = text.split("\n")
        for line in lines:
            parts = re.split(r"\s{2,}", line)
            if len(parts) == 3:
                desc = parts[0]
                qty = self.safe_float(parts[1])
                total = self.safe_float(parts[2])
                if qty is not None and total is not None:
                    unit = total / qty if qty else None
                    items.append(LineItem(description=desc, quantity=qty,
                                          unit_price=unit or 0, line_total=total))
        return items

    def safe_float(self, v):
        try:
            return float(v.replace(",", ""))
        except:
            return None
