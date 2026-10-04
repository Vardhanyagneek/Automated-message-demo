import json
import os
import time

import requests
from dotenv import load_dotenv

# override=True makes the .env file win over any old value stored in Windows
load_dotenv(override=True)


def _clean(value):
    """Remove spaces, quotes and line breaks accidentally copied into .env."""
    return (value or "").strip().strip('"').strip("'").strip()


DELAY_SECONDS = 1  # pause between messages

TOKEN = _clean(os.getenv("WHATSAPP_TOKEN"))
PHONE_ID = _clean(os.getenv("PHONE_NUMBER_ID"))
API_VERSION = _clean(os.getenv("API_VERSION")) or "v25.0"
TEMPLATE_NAME = _clean(os.getenv("TEMPLATE_NAME")) or "hello_world"
TEMPLATE_LANG = _clean(os.getenv("TEMPLATE_LANG")) or "en_US"
# template = approved template (works any time)
# text     = personalized text (only inside the 24-hour window after the person messaged you)
SEND_MODE = (_clean(os.getenv("SEND_MODE")) or "template").lower()

# Friendly explanations for common Meta error codes
ERROR_HELP = {
    190: "Access token is invalid or expired. Generate a new token in Meta and paste it into .env.",
    131030: "Recipient is not in the allowed list. Add and verify this number in Meta (API Setup).",
    131047: "More than 24 hours since the customer last messaged you. Use SEND_MODE=template.",
    131026: "Message could not be delivered (number may not be on WhatsApp).",
    100: "Invalid parameter. Check PHONE_NUMBER_ID and the phone number format.",
}


def check_setup():
    """Print a safe summary of what was loaded from .env (token is never printed)."""
    print(f"Token loaded: {len(TOKEN)} characters | Phone ID: {PHONE_ID or 'MISSING'} "
          f"| API {API_VERSION} | Send mode: {SEND_MODE}")
    if TOKEN and (len(TOKEN) < 100 or " " in TOKEN):
        print("WARNING: token looks too short or has spaces. Re-copy it from Meta.")
    if not TOKEN or TOKEN.startswith("paste"):
        print("WARNING: WHATSAPP_TOKEN in .env is empty or still a placeholder.")


def send_message(contact, message, mock=True):
    """Send one message. Returns (status, detail)."""
    if mock:
        print(f"[MOCK] Sent to {contact['phone']}: {message}")
        return "sent", "mock mode"

    if not TOKEN or not PHONE_ID:
        return "failed", "Missing WHATSAPP_TOKEN or PHONE_NUMBER_ID in .env"

    url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

    if SEND_MODE == "text":
        payload = {
            "messaging_product": "whatsapp",
            "to": contact["phone"],
            "type": "text",
            "text": {"body": message},
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": contact["phone"],
            "type": "template",
            "template": {"name": TEMPLATE_NAME, "language": {"code": TEMPLATE_LANG}},
        }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code == 200:
            msg_id = r.json()["messages"][0]["id"]
            print(f"[REAL/{SEND_MODE}] Sent to {contact['phone']} (id {msg_id})")
            return "sent", f"{SEND_MODE}: {msg_id}"

        try:
            err = r.json().get("error", {})
        except (ValueError, AttributeError):
            err = {}
        code = err.get("code")
        reason = ERROR_HELP.get(code, err.get("message", r.text[:150]))
        print(f"[REAL/{SEND_MODE}] Failed for {contact['phone']} (code {code}): {reason}")
        return "failed", f"code {code}: {reason}"
    except requests.RequestException as e:
        return "failed", str(e)


def pause():
    time.sleep(DELAY_SECONDS)