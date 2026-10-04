import os

from dotenv import load_dotenv

from contacts_loader import load_contacts
from templates import build_message
from sender import send_message, pause, check_setup
from logger import log_result

load_dotenv(override=True)
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
print(f"Mode: {'MOCK' if MOCK_MODE else 'REAL'}")
if not MOCK_MODE:
    check_setup()
print()

contacts, skipped = load_contacts("contacts.csv")

# Log contacts that were skipped
for name, phone, reason in skipped:
    log_result(name, phone, "skipped", reason)

# Send to valid contacts
counts = {"sent": 0, "failed": 0}
for c in contacts:
    message = build_message(c)
    status, detail = send_message(c, message, mock=MOCK_MODE)
    log_result(c["name"], c["phone"], status, detail)
    counts[status] += 1
    pause()

print("\n--- Summary ---")
print(f"Sent: {counts['sent']}  Failed: {counts['failed']}  Skipped: {len(skipped)}")
print("Details saved in results.csv")