"""Message templates with {placeholders}, chosen by contact tag."""

PROMO = ("Hi {name}, Health Pilot has a special offer for you: "
         "20% off your next order with code THANKS20.")

TEMPLATES = {
    "customer": PROMO,
    "lead": PROMO,
    "default": PROMO,
}


def build_message(contact):
    """Pick a template by the contact's first tag and fill in placeholders."""
    tag = contact["tags"].split(",")[0].strip().lower()
    template = TEMPLATES.get(tag, TEMPLATES["default"])
    return template.format(name=contact["name"])
