from .schemas import Invoice
from datetime import datetime

class InvoiceValidator:
    def __init__(self):
        self.seen_keys = set()

    def _parse_date(self, d):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(d, fmt)
            except:
                continue
        return None

    def _validate_completeness(self, inv, errors):
        required = ["invoice_number", "invoice_date", "seller_name", "buyer_name"]
        for f in required:
            if not getattr(inv, f):
                errors.append(f"missing_field: {f}")

    def _validate_format(self, inv, errors):
        if inv.invoice_date and not self._parse_date(inv.invoice_date):
            errors.append("invalid_format: invoice_date")
        if inv.currency and inv.currency not in ["INR", "USD", "EUR", "GBP"]:
            errors.append("invalid_format: currency")

    def _validate_business(self, inv, errors):
        if inv.line_items:
            calc = sum([i.line_total for i in inv.line_items if i.line_total])
            if inv.net_total and abs(calc - inv.net_total) > 1:
                errors.append("business_rule_failed: line_items_sum_mismatch")

        if inv.net_total and inv.tax_amount and inv.gross_total:
            if abs(inv.net
