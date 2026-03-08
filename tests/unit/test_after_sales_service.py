from __future__ import annotations

import unittest
from types import SimpleNamespace
from collections import Counter

from helpers import build_frappe_env


class TestAfterSalesService(unittest.TestCase):
    def setUp(self):
        self.env = build_frappe_env()

    def tearDown(self):
        self.env.cleanup()

    def test_determine_after_sales_decision_status_maps_ticket_types(self):
        module = self.env.load_module("fashion_erp.stock.services.after_sales_service")

        self.assertEqual(
            module._determine_after_sales_decision_status(SimpleNamespace(ticket_type="仅退款")),
            "待退款",
        )
        self.assertEqual(
            module._determine_after_sales_decision_status(SimpleNamespace(ticket_type="换货")),
            "待补发",
        )
        self.assertEqual(
            module._determine_after_sales_decision_status(SimpleNamespace(ticket_type="投诉")),
            "待处理",
        )

    def test_validate_items_reuses_cached_sales_order_item_and_item_meta(self):
        module = self.env.load_module("fashion_erp.stock.services.after_sales_service")
        self.env.db.exists_map.update(
            {
                ("Item", "FG-001"): True,
                ("Style", "ST-001"): True,
            }
        )
        self.env.db.value_map[
            (
                "Sales Order Item",
                "SOI-001",
                ("parent", "item_code", "style", "color_code", "size_code", "rate", "uom", "warehouse", "delivery_date"),
                True,
            )
        ] = {
            "parent": "SO-001",
            "item_code": "FG-001",
            "style": "ST-001",
            "color_code": "BLK",
            "size_code": "M",
            "rate": 99,
            "uom": "Nos",
            "warehouse": "WH-01",
            "delivery_date": "2026-03-10",
        }
        self.env.db.value_map[
            ("Item", "FG-001", ("style", "color_code", "size_code"), True)
        ] = {
            "style": "ST-001",
            "color_code": "BLK",
            "size_code": "M",
        }
        lookup_counter = Counter()
        original_get_value = self.env.db.get_value

        def counting_get_value(doctype, name, fieldname, as_dict=False):
            frozen_field = tuple(fieldname) if isinstance(fieldname, list) else fieldname
            lookup_counter[(doctype, name, frozen_field, as_dict)] += 1
            return original_get_value(doctype, name, fieldname, as_dict=as_dict)

        self.env.db.get_value = counting_get_value
        doc = SimpleNamespace(
            flags=SimpleNamespace(),
            ticket_type="退货退款",
            sales_order="",
            delivery_note="",
            return_reason="",
            return_disposition="",
            items=[
                SimpleNamespace(
                    idx=1,
                    sales_order_item_ref="SOI-001",
                    delivery_note_item_ref="",
                    item_code="",
                    style="",
                    color_code="",
                    size_code="",
                    requested_action="",
                    qty=1,
                    received_qty=0,
                    restock_qty=0,
                    defective_qty=0,
                    inspection_note="",
                    return_reason="",
                    return_disposition="",
                    inventory_status_from="",
                    inventory_status_to="",
                ),
                SimpleNamespace(
                    idx=2,
                    sales_order_item_ref="SOI-001",
                    delivery_note_item_ref="",
                    item_code="",
                    style="",
                    color_code="",
                    size_code="",
                    requested_action="",
                    qty=1,
                    received_qty=0,
                    restock_qty=0,
                    defective_qty=0,
                    inspection_note="",
                    return_reason="",
                    return_disposition="",
                    inventory_status_from="",
                    inventory_status_to="",
                ),
            ],
        )

        module._validate_items(doc)

        self.assertEqual(doc.sales_order, "SO-001")
        self.assertEqual(doc.items[0].item_code, "FG-001")
        self.assertEqual(doc.items[1].item_code, "FG-001")
        self.assertEqual(
            lookup_counter[
                (
                    "Sales Order Item",
                    "SOI-001",
                    ("parent", "item_code", "style", "color_code", "size_code", "rate", "uom", "warehouse", "delivery_date"),
                    True,
                )
            ],
            1,
        )
        self.assertEqual(
            lookup_counter[
                ("Item", "FG-001", ("style", "color_code", "size_code"), True)
            ],
            1,
        )

    def test_build_replacement_sales_order_items_reuses_cached_sales_order_item_rows(self):
        module = self.env.load_module("fashion_erp.stock.services.after_sales_service")
        self.env.meta_fields["Sales Order Item"] = {
            "item_code",
            "qty",
            "rate",
            "uom",
            "delivery_date",
            "warehouse",
            "style",
            "color_code",
            "size_code",
        }
        self.env.db.value_map[
            (
                "Sales Order Item",
                "SOI-002",
                ("parent", "item_code", "style", "color_code", "size_code", "rate", "uom", "warehouse", "delivery_date"),
                True,
            )
        ] = {
            "parent": "SO-002",
            "item_code": "FG-002",
            "style": "ST-002",
            "color_code": "WHT",
            "size_code": "L",
            "rate": 129,
            "uom": "Nos",
            "warehouse": "WH-SO",
            "delivery_date": "2026-03-12",
        }
        lookup_counter = Counter()
        original_get_value = self.env.db.get_value

        def counting_get_value(doctype, name, fieldname, as_dict=False):
            frozen_field = tuple(fieldname) if isinstance(fieldname, list) else fieldname
            lookup_counter[(doctype, name, frozen_field, as_dict)] += 1
            return original_get_value(doctype, name, fieldname, as_dict=as_dict)

        self.env.db.get_value = counting_get_value
        doc = SimpleNamespace(
            flags=SimpleNamespace(),
            warehouse="WH-RET",
            items=[
                SimpleNamespace(
                    requested_action="补发",
                    sales_order_item_ref="SOI-002",
                    qty=1,
                    received_qty=0,
                    item_code="FG-002",
                    style="ST-002",
                    color_code="WHT",
                    size_code="L",
                ),
                SimpleNamespace(
                    requested_action="补发",
                    sales_order_item_ref="SOI-002",
                    qty=2,
                    received_qty=0,
                    item_code="FG-002",
                    style="ST-002",
                    color_code="WHT",
                    size_code="L",
                ),
            ],
        )

        module._reset_after_sales_validation_cache(doc)
        items = module._build_replacement_sales_order_items(doc, set_warehouse="")

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["rate"], 129)
        self.assertEqual(items[0]["uom"], "Nos")
        self.assertEqual(items[0]["delivery_date"], "2026-03-12")
        self.assertEqual(items[0]["warehouse"], "WH-SO")
        self.assertEqual(items[1]["qty"], 2.0)
        self.assertEqual(
            lookup_counter[
                (
                    "Sales Order Item",
                    "SOI-002",
                    ("parent", "item_code", "style", "color_code", "size_code", "rate", "uom", "warehouse", "delivery_date"),
                    True,
                )
            ],
            1,
        )

    def test_after_sales_header_sync_reuses_cached_sales_order_and_context_queries(self):
        module = self.env.load_module("fashion_erp.stock.services.after_sales_service")
        self.env.db.value_map.update(
            {
                (
                    "Sales Order",
                    "SO-001",
                    (
                        "customer",
                        "customer_name",
                        "channel",
                        "channel_store",
                        "external_order_id",
                        "company",
                        "delivery_date",
                    ),
                    True,
                ): {
                    "customer": "CUST-001",
                    "customer_name": "张三",
                    "channel": "抖音",
                    "channel_store": "STORE-01",
                    "external_order_id": "EXT-001",
                    "company": "COMP-01",
                    "delivery_date": "2026-03-10",
                },
                ("Channel Store", "STORE-01", "channel", False): "抖音",
                ("Warehouse Location", "LOC-01", "warehouse", False): "WH-01",
            }
        )
        lookup_counter = Counter()
        original_get_value = self.env.db.get_value

        def counting_get_value(doctype, name, fieldname, as_dict=False):
            frozen_field = tuple(fieldname) if isinstance(fieldname, list) else fieldname
            lookup_counter[(doctype, name, frozen_field, as_dict)] += 1
            return original_get_value(doctype, name, fieldname, as_dict=as_dict)

        self.env.db.get_value = counting_get_value
        doc = SimpleNamespace(
            flags=SimpleNamespace(),
            sales_order="SO-001",
            sales_invoice="",
            delivery_note="",
            customer="",
            buyer_name="",
            channel="",
            channel_store="",
            external_order_id="",
            warehouse="",
            warehouse_location="LOC-01",
        )

        module._reset_after_sales_validation_cache(doc)
        module._sync_from_sales_order(doc)
        module._sync_from_sales_order(doc)
        module._sync_location_context(doc)
        module._sync_location_context(doc)

        self.assertEqual(module._get_after_sales_company(doc), "COMP-01")
        self.assertEqual(module._get_after_sales_company(doc), "COMP-01")
        self.assertEqual(module._get_after_sales_delivery_date(doc), "2026-03-10")
        self.assertEqual(module._get_after_sales_delivery_date(doc), "2026-03-10")

        self.assertEqual(doc.customer, "CUST-001")
        self.assertEqual(doc.buyer_name, "张三")
        self.assertEqual(doc.channel_store, "STORE-01")
        self.assertEqual(doc.external_order_id, "EXT-001")
        self.assertEqual(doc.warehouse, "WH-01")
        self.assertEqual(
            lookup_counter[
                (
                    "Sales Order",
                    "SO-001",
                    (
                        "customer",
                        "customer_name",
                        "channel",
                        "channel_store",
                        "external_order_id",
                        "company",
                        "delivery_date",
                    ),
                    True,
                )
            ],
            1,
        )
        self.assertEqual(lookup_counter[("Channel Store", "STORE-01", "channel", False)], 1)
        self.assertEqual(lookup_counter[("Warehouse Location", "LOC-01", "warehouse", False)], 1)

    def test_after_sales_default_company_and_stock_entry_type_reuse_cached_exists_checks(self):
        module = self.env.load_module("fashion_erp.stock.services.after_sales_service")
        self.env.frappe.defaults = SimpleNamespace(
            get_user_default=lambda key: "COMP-01" if key == "Company" else "",
            get_global_default=lambda _key: "",
        )
        self.env.db.exists_map.update(
            {
                ("Company", "COMP-01"): True,
                ("Stock Entry Type", "Material Receipt"): True,
            }
        )
        self.env.meta_fields["Stock Entry"] = {
            "purpose",
            "stock_entry_type",
            "company",
            "after_sales_ticket",
            "from_warehouse",
            "to_warehouse",
            "remarks",
            "items",
        }
        exists_counter = Counter()
        original_exists = self.env.db.exists

        def counting_exists(doctype, name):
            exists_counter[(doctype, name)] += 1
            return original_exists(doctype, name)

        self.env.db.exists = counting_exists
        doc = SimpleNamespace(
            flags=SimpleNamespace(),
            name="TK-001",
            sales_order="",
        )

        module._reset_after_sales_validation_cache(doc)
        self.assertEqual(module._get_after_sales_company(doc), "COMP-01")
        self.assertEqual(module._get_after_sales_company(doc), "COMP-01")
        module._build_after_sales_stock_entry_payload(
            doc,
            company="COMP-01",
            purpose="Material Receipt",
            source_warehouse="",
            target_warehouse="WH-RET",
            remark="",
            entry_mode="待检入库",
            items=[],
        )
        module._build_after_sales_stock_entry_payload(
            doc,
            company="COMP-01",
            purpose="Material Receipt",
            source_warehouse="",
            target_warehouse="WH-RET",
            remark="",
            entry_mode="待检入库",
            items=[],
        )

        self.assertEqual(exists_counter[("Company", "COMP-01")], 1)
        self.assertEqual(exists_counter[("Stock Entry Type", "Material Receipt")], 1)


if __name__ == "__main__":
    unittest.main()
