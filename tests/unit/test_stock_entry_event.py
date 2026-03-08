from __future__ import annotations

import unittest
from types import SimpleNamespace

from helpers import FakeDoc, build_frappe_env


class TestStockEntryEvent(unittest.TestCase):
    def setUp(self):
        self.env = build_frappe_env()

    def tearDown(self):
        self.env.cleanup()

    def test_validate_inventory_status_rules_syncs_header_delivery_note_to_rows(self):
        module = self.env.load_module("fashion_erp.stock.events.stock_entry")
        doc = FakeDoc(
            delivery_note="DN-001",
            items=[
                SimpleNamespace(
                    item_code="PKG-001",
                    delivery_note="",
                    inventory_status_from="",
                    inventory_status_to="",
                    return_reason="",
                    return_disposition="",
                )
            ],
        )

        module.validate_inventory_status_rules(doc)

        self.assertEqual(doc.items[0].delivery_note, "DN-001")

    def test_validate_inventory_status_rules_promotes_row_delivery_note_to_header(self):
        module = self.env.load_module("fashion_erp.stock.events.stock_entry")
        doc = FakeDoc(
            delivery_note="",
            items=[
                SimpleNamespace(
                    item_code="PKG-001",
                    delivery_note="DN-002",
                    inventory_status_from="",
                    inventory_status_to="",
                    return_reason="",
                    return_disposition="",
                )
            ],
        )

        module.validate_inventory_status_rules(doc)

        self.assertEqual(doc.delivery_note, "DN-002")


if __name__ == "__main__":
    unittest.main()
