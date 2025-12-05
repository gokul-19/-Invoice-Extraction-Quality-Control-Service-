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
            if abs(inv.net_total + inv.tax_amount - inv.gross_total) > 1:
                errors.append("business_rule_failed: totals_mismatch")

        d1 = self._parse_date(inv.invoice_date)
        d2 = self._parse_date(inv.due_date) if inv.due_date else None
        if d1 and d2 and d2 < d1:
            errors.append("business_rule_failed: due_before_invoice")

    def _validate_anomaly(self, inv, errors):
        key = (inv.invoice_number, inv.seller_name)
        if inv.invoice_number and key in self.seen_keys:
            errors.append("anomaly: duplicate_invoice")
        else:
            if inv.invoice_number:
                self.seen_keys.add(key)

        nums = [inv.net_total, inv.tax_amount, inv.gross_total]
        if any(n is not None and n < 0 for n in nums):
            errors.append("anomaly: negative_amount")

    def validate(self, invoices):
        results = []
        err_counts = {}

        for inv in invoices:
            invoice = Invoice(**inv) if isinstance(inv, dict) else inv
            errors = []

            self._validate_completeness(invoice, errors)
            self._validate_format(invoice, errors)
            self._validate_business(invoice, errors)
            self._validate_anomaly(invoice, errors)

            for e in errors:
                err_counts[e] = err_counts.get(e, 0) + 1

            results.append({
                "invoice_id": invoice.invoice_number,
                "is_valid": len(errors) == 0,
                "errors": errors
            })

        summary = {
            "total_invoices": len(invoices),
            "valid_invoices": sum(1 for r in results if r["is_valid"]),
            "invalid_invoices": sum(1 for r in results if not r["is_valid"]),
            "error_counts": err_counts
        }

        return {"results": results, "summary": summary}

