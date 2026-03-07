frappe.ui.form.on("Style", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Generate Variants"), () => {
			runStyleAction(frm, "fashion_erp.style.api.generate_variants");
		});

		frm.add_custom_button(__("Create Template Item"), () => {
			runStyleAction(frm, "fashion_erp.style.api.create_template_item");
		});

		frm.add_custom_button(__("Open Matrix"), () => {
			openStyleMatrix(frm);
		});

		frm.add_custom_button(__("Create Production Ticket"), () => {
			createProductionTicket(frm);
		});
	},

	colors_add(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.sort_order) {
			frappe.model.set_value(cdt, cdn, "sort_order", (frm.doc.colors || []).length * 10);
		}
		if (row.enabled === undefined || row.enabled === null) {
			frappe.model.set_value(cdt, cdn, "enabled", 1);
		}
	}
});

frappe.ui.form.on("Style Color", {
	color(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.color) {
			return;
		}

		frappe.db.get_value("Color", row.color, ["color_name", "color_group"]).then((response) => {
			const colorDoc = response.message || {};
			frappe.model.set_value(cdt, cdn, "color_name", colorDoc.color_name || row.color);

			if (!colorDoc.color_group) {
				return null;
			}

			return frappe.db.get_value("Color Group", colorDoc.color_group, "color_group_code").then((groupResponse) => {
				const groupDoc = groupResponse.message || {};
				frappe.model.set_value(cdt, cdn, "color_code", groupDoc.color_group_code || "");
			});
		});
	}
});

function runStyleAction(frm, method) {
	frappe.call({
		method,
		args: {
			style_name: frm.doc.name
		}
	}).then((response) => {
		const payload = response.message || {};
		let message = payload.message || __("Action completed.");
		if (payload.issues && payload.issues.length) {
			message += "<br><br>" + payload.issues.map((issue) => `- ${issue}`).join("<br>");
		}
		frappe.msgprint(message);
	});
}

function openStyleMatrix(frm) {
	frappe.call({
		method: "fashion_erp.style.api.get_style_matrix",
		args: {
			style_name: frm.doc.name
		}
	}).then((response) => {
		const payload = response.message || {};
		if (!payload.ok) {
			let message = payload.message || __("Unable to load Style Matrix.");
			if (payload.issues && payload.issues.length) {
				message += "<br><br>" + payload.issues.map((issue) => `- ${issue}`).join("<br>");
			}
			frappe.msgprint(message);
			return;
		}

		const matrix = payload.result || {};
		const dialog = new frappe.ui.Dialog({
			title: `${__("Style Matrix")} - ${frm.doc.style_code || frm.doc.name}`,
			size: "extra-large",
			fields: [
				{
					fieldname: "matrix_html",
					fieldtype: "HTML"
				}
			]
		});

		dialog.fields_dict.matrix_html.$wrapper.html(renderStyleMatrix(matrix));
		dialog.show();
	});
}

function createProductionTicket(frm) {
	const defaults = {
		style: frm.doc.name,
		item_template: frm.doc.item_template || ""
	};
	const enabledColors = (frm.doc.colors || []).filter((row) => Number(row.enabled || 0) === 1);
	if (enabledColors.length === 1) {
		defaults.color = enabledColors[0].color;
	}
	frappe.new_doc("Production Ticket", defaults);
}

function renderStyleMatrix(matrix) {
	const sizeRows = matrix.size_rows || [];
	const matrixRows = matrix.matrix_rows || [];
	const summary = matrix.summary || {};
	const issues = matrix.issues || [];

	let html = `
		<div style="margin-bottom: 12px;">
			<div><strong>${escapeHtml(matrix.style_name || "")}</strong> (${escapeHtml(matrix.style_code || "")})</div>
			<div>${__("SKU Prefix")}: <strong>${escapeHtml(matrix.brand_prefix || "")}</strong></div>
			<div>${__("Generated")}: <strong>${summary.existing_count || 0}</strong> / ${summary.total_count || 0}</div>
			<div>${__("Missing")}: <strong style="color:#b42318;">${summary.missing_count || 0}</strong></div>
		</div>
	`;

	if (issues.length) {
		html += `
			<div style="margin-bottom: 12px; padding: 10px; background: #fff4e5; border: 1px solid #f5c36b; border-radius: 6px;">
				<div style="font-weight: 600; margin-bottom: 6px;">${__("Prerequisite Issues")}</div>
				${issues.map((issue) => `<div>- ${escapeHtml(issue)}</div>`).join("")}
			</div>
		`;
	}

	html += `<div style="overflow:auto;"><table class="table table-bordered" style="min-width: 900px;">`;
	html += `<thead><tr><th>${__("Color")}</th>`;
	sizeRows.forEach((sizeRow) => {
		html += `<th>${escapeHtml(sizeRow.size_name || sizeRow.size_code || "")}</th>`;
	});
	html += `</tr></thead><tbody>`;

	matrixRows.forEach((row) => {
		html += `<tr>`;
		html += `<td><strong>${escapeHtml(row.color_name || "")}</strong><br><span class="text-muted">${escapeHtml(row.color_code || "")}</span></td>`;

		(row.cells || []).forEach((cell) => {
			const bg = cell.exists ? "#ecfdf3" : "#fef3f2";
			const border = cell.exists ? "#6ce9a6" : "#fda29b";
			const label = cell.exists ? __("Exists") : __("Missing");
			const sellableText = cell.exists ? (cell.sellable ? __("Sellable") : __("Not Sellable")) : "";
			const qtyText = cell.exists ? `${__("Stock")}: ${formatNumber(cell.stock_qty)}` : "";
			html += `
				<td style="background:${bg}; border-color:${border}; min-width: 130px;">
					<div style="font-weight:600;">${escapeHtml(cell.sku_code || "")}</div>
					<div style="font-size:12px; color:${cell.exists ? "#067647" : "#b42318"};">${label}</div>
					${sellableText ? `<div style="font-size:12px;" class="text-muted">${escapeHtml(sellableText)}</div>` : ""}
					${qtyText ? `<div style="font-size:12px;" class="text-muted">${escapeHtml(qtyText)}</div>` : ""}
					${cell.item_name ? `<div style="font-size:12px;" class="text-muted">${escapeHtml(cell.item_name)}</div>` : ""}
				</td>
			`;
		});

		html += `</tr>`;
	});

	html += `</tbody></table></div>`;
	return html;
}

function escapeHtml(value) {
	return String(value || "")
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#39;");
}

function formatNumber(value) {
	return Number(value || 0).toLocaleString(undefined, {
		maximumFractionDigits: 2
	});
}
