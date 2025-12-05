import pdfplumber
import re
import os
import yaml
import json
from .schemas import Invoice, LineItem

class InvoiceExtractor:
    def __init__(self):
        cfg_dir = os.path.join(os.path.dirname(__file__), "config")
        with open(os.path.join(cfg_dir, "patterns.yaml")) as f:
            self.patterns = yaml.safe_load(f)
        with open(os.path.join(cfg_dir, "currency_list.json")) as f:
            self.valid_currencies = json.load(f)

    def _find_value(self, text, labels):
        for label in labels:
            pattern = rf"{label}\s*[:\-]?\s*(.+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_line_items(self, text):
        items = []
        lines = text.split("\n")
        for line in lines:
            parts = re.split(r"\s{2,}", line.strip())
            if len(parts) >= 4:
                desc, qty, price, total = parts[:4]
                if re.match(r"^\d+(\.\d+)?$", qty) and re.match(r"^\d+(\.\d+)?$", price):
                    items.append(
                        LineItem(
                            description=desc,
                            quantity=float(qty),
                            unit_price=float(price),
                            line_total=float(total) if total.replace(".", "", 1).isdigit() else None
                        )
                    )
        return items

    def extract_single(self, pdf_file):
        # pdf_file can be BytesIO from Streamlit upload
        with pdfplumber.open(pdf_file) as pdf:
            pages_text = "\n".join([p.extract_text() or "" for p in pdf.pages])

        data = {}
        for key, labels in self.patterns.items():
            data[key] = self._find_value(pages_text, labels)

        for f in ["net_total", "tax_amount", "gross_total"]:
            if data.get(f) and re.match(r"^\d+(\.\d+)?$", str(data[f])):
                data[f] = float(data[f])
            else:
                data[f] = None

        data["currency"] = next((c for c in self.valid_currencies if c in pages_text), None)
        data["line_items"] = self._extract_line_items(pages_text)

        return Invoice(**data)

