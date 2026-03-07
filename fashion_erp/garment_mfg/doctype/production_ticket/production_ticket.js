frappe.ui.form.on("Production Ticket", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		if (!["Completed", "Cancelled"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Add Stage Log"), () => {
				openStageLogDialog(frm);
			});
		}

		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Start"), () => {
				runTicketAction(frm, "start_ticket");
			});
		}

		if (!["Completed", "Cancelled"].includes(frm.doc.status) && frm.doc.stage !== "Done") {
			frm.add_custom_button(__("Next Stage"), () => {
				runTicketAction(frm, "next_stage");
			});
		}

		if (frm.doc.status === "In Progress") {
			frm.add_custom_button(__("Hold"), () => {
				runTicketAction(frm, "hold_ticket");
			});
		}

		if (frm.doc.status === "Hold") {
			frm.add_custom_button(__("Resume"), () => {
				runTicketAction(frm, "resume_ticket");
			});
		}

		if (!["Completed", "Cancelled"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Complete"), () => {
				runTicketAction(frm, "complete_ticket");
			});
		}
	},

	style(frm) {
		if (!frm.doc.style) {
			return;
		}

		frappe.db.get_value("Style", frm.doc.style, "item_template").then((response) => {
			const styleDoc = response.message || {};
			if (styleDoc.item_template && !frm.doc.item_template) {
				frm.set_value("item_template", styleDoc.item_template);
			}
		});
	},

	color(frm) {
		if (!frm.doc.color) {
			frm.set_value("color_name", "");
			frm.set_value("color_code", "");
			return;
		}

		frappe.db.get_value("Color", frm.doc.color, ["color_name", "color_group"]).then((response) => {
			const colorDoc = response.message || {};
			frm.set_value("color_name", colorDoc.color_name || frm.doc.color);

			if (!colorDoc.color_group) {
				frm.set_value("color_code", "");
				return null;
			}

			return frappe.db.get_value("Color Group", colorDoc.color_group, "color_group_code").then((groupResponse) => {
				const groupDoc = groupResponse.message || {};
				frm.set_value("color_code", groupDoc.color_group_code || "");
			});
		});
	}
});

function runTicketAction(frm, method, args = {}) {
	const invoke = () => frm.call(method, args).then((response) => {
		const payload = response.message || {};
		if (payload.message) {
			frappe.show_alert({
				message: payload.message,
				indicator: "green"
			});
		}
		return frm.reload_doc();
	});

	if (frm.is_dirty()) {
		return frm.save().then(() => invoke());
	}

	return invoke();
}

function openStageLogDialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __("Add Stage Log"),
		fields: [
			{
				fieldname: "stage",
				fieldtype: "Select",
				label: "Stage",
				options: "Planned\nCutting\nStitching\nFinishing\nPacking\nDone",
				reqd: 1,
				default: frm.doc.stage || "Planned"
			},
			{
				fieldname: "qty_in",
				fieldtype: "Int",
				label: "Qty In",
				default: frm.doc.qty || 0
			},
			{
				fieldname: "qty_out",
				fieldtype: "Int",
				label: "Qty Out",
				default: frm.doc.qty || 0
			},
			{
				fieldname: "defect_qty",
				fieldtype: "Int",
				label: "Defect Qty",
				default: 0
			},
			{
				fieldname: "warehouse",
				fieldtype: "Link",
				label: "Warehouse",
				options: "Warehouse"
			},
			{
				fieldname: "supplier",
				fieldtype: "Link",
				label: "Supplier",
				options: "Supplier",
				default: frm.doc.supplier || ""
			},
			{
				fieldname: "remark",
				fieldtype: "Small Text",
				label: "Remark"
			}
		]
	});

	dialog.set_primary_action(__("Save"), () => {
		const values = dialog.get_values();
		if (!values) {
			return;
		}

		runTicketAction(frm, "add_stage_log", values).then(() => {
			dialog.hide();
		});
	});

	dialog.show();
}
