import frappe
from frappe.model.document import Document

from fashion_erp.garment_mfg.services.production_service import (
    add_stage_log_to_ticket,
    advance_production_ticket_stage,
    complete_production_ticket,
    hold_production_ticket,
    resume_production_ticket,
    start_production_ticket,
    validate_production_ticket,
)


class ProductionTicket(Document):
    def validate(self) -> None:
        validate_production_ticket(self)

    @frappe.whitelist()
    def start_ticket(self) -> dict[str, object]:
        return _run_and_reload(self, start_production_ticket)

    @frappe.whitelist()
    def next_stage(self) -> dict[str, object]:
        return _run_and_reload(self, advance_production_ticket_stage)

    @frappe.whitelist()
    def hold_ticket(self) -> dict[str, object]:
        return _run_and_reload(self, hold_production_ticket)

    @frappe.whitelist()
    def resume_ticket(self) -> dict[str, object]:
        return _run_and_reload(self, resume_production_ticket)

    @frappe.whitelist()
    def complete_ticket(self) -> dict[str, object]:
        return _run_and_reload(self, complete_production_ticket)

    @frappe.whitelist()
    def add_stage_log(
        self,
        stage: str | None = None,
        qty_in: int | str | None = None,
        qty_out: int | str | None = None,
        defect_qty: int | str | None = None,
        warehouse: str | None = None,
        supplier: str | None = None,
        remark: str | None = None,
    ) -> dict[str, object]:
        payload = add_stage_log_to_ticket(
            self.name,
            stage=stage,
            qty_in=qty_in,
            qty_out=qty_out,
            defect_qty=defect_qty,
            warehouse=warehouse,
            supplier=supplier,
            remark=remark,
        )
        self.reload()
        return payload


def _run_and_reload(doc: Document, action) -> dict[str, object]:
    payload = action(doc.name)
    doc.reload()
    return payload
