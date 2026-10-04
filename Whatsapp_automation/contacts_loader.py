import re
import pandas as pd


def load_contacts(path):
    """Return (valid_contacts, skipped). Skips unsubscribed and invalid numbers."""
    df = pd.read_csv(path, dtype=str).fillna("")
    contacts, skipped = [], []

    for _, row in df.iterrows():
        phone = re.sub(r"\D", "", row["phone"])  # keep digits only

        if row["subscribed"].strip().lower() != "yes":
            skipped.append((row["name"], phone, "unsubscribed"))
        elif not (10 <= len(phone) <= 15):
            skipped.append((row["name"], phone, "invalid phone"))
        else:
            contacts.append({
                "name": row["name"].strip(),
                "phone": phone,
                "tags": row["tags"].strip(),
            })

    return contacts, skipped