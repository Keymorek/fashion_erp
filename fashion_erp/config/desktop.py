from frappe import _


def get_data():
    return [
        {
            "module_name": "Style",
            "color": "blue",
            "icon": "octicon octicon-tag",
            "type": "module",
            "label": _("Style"),
        },
        {
            "module_name": "Channel",
            "color": "green",
            "icon": "octicon octicon-broadcast",
            "type": "module",
            "label": _("Channel"),
        },
        {
            "module_name": "Garment Mfg",
            "color": "orange",
            "icon": "octicon octicon-tools",
            "type": "module",
            "label": _("Garment Mfg"),
        },
    ]
