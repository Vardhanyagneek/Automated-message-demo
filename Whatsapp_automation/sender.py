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
# Comma-separated contacts.csv columns that fill {{1}}, {{2}}, ... in your approved template.
# Example: TEMPLATE_VARS=name,bmi,bmi_category,sugar,sugar_test,bp
TEMPLATE_VARS = [v.strip() for v in (os.getenv("TEMPLATE_VARS") or "").split(",") if v.strip()]
# Meta's sample "hello_world" template has no variables, so never send any with it.
if TEMPLATE_NAME == "hello_world":
    TEMPLATE_VARS = []

# Friendly explanations for common Meta error codes
ERROR_HELP = {
    190: "Access token is invalid or expired. Generate a new token in Meta and paste it into .env.",
    131030: "Recipient is not in the allowed list. Add and verify this number in Meta (API Setup).",
    131047: "More than 24 hours since the customer last messaged you. Use SEND_MODE=template.",
    131026: "Message could not be delivered (number may not be on WhatsApp).",
    132000: "Template variable count does not match. Clear TEMPLATE_VARS or fix it in .env.",
    132001: "Template name or language not found. Check TEMPLATE_NAME and TEMPLATE_LANG in .env.",
    100: "Invalid parameter. Check PHONE_NUMBER_ID and the phone number format.",
}


def check_setup():
    """Print a safe summary of what was loaded from .env (token is never printed)."""
    line = (f"Token loaded: {len(TOKEN)} characters | Phone ID: {PHONE_ID or 'MISSING'} "
            f"| API {API_VERSION} | Send mode: {SEND_MODE}")
    if SEND_MODE == "template":
        line += f" | Template: {TEMPLATE_NAME} ({len(TEMPLATE_VARS)} variables)"
    print(line)
    if TOKEN and (len(TOKEN) < 100 or " " in TOKEN):
        print("WARNING: token looks too short or has spaces. Re-copy it from Meta.")
    if not TOKEN or TOKEN.startswith("paste") or TOKEN.startswith("your_"):
        print("WARNING: WHATSAPP_TOKEN in .env is empty or still a placeholder.")
    if not PHONE_ID.isdigit():
        print("WARNING: PHONE_NUMBER_ID should be digits only (for the test number: 1371173202745578).")
    if SEND_MODE == "text":
        print("NOTE: text mode only delivers if your phone messaged the test number in the last 24 hours.\n"
              "      Send 'hi' to the test number, then run again.")


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
        template = {"name": TEMPLATE_NAME, "language": {"code": TEMPLATE_LANG}}
        if TEMPLATE_VARS:
            missing = [v for v in TEMPLATE_VARS if not str(contact.get(v, "")).strip()]
            if missing:
                return "failed", f"contacts.csv is missing values for: {', '.join(missing)}"
            template["components"] = [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": " ".join(str(contact[v]).split())}
                    for v in TEMPLATE_VARS
                ],
            }]
        payload = {
            "messaging_product": "whatsapp",
            "to": contact["phone"],
            "type": "template",
            "template": template,
        }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            msg_id = data["messages"][0]["id"]
            # wa_id is the number Meta actually used; it should match the contact's number
            wa_id = (data.get("contacts") or [{}])[0].get("wa_id", "")
            status = data["messages"][0].get("message_status", "")
            print(f"[REAL/{SEND_MODE}] Accepted for {wa_id or contact['phone']} "
                  f"(id {msg_id}{', ' + status if status else ''})")
            if wa_id and wa_id != contact["phone"]:
                print(f"  NOTE: Meta used {wa_id}, but contacts.csv has {contact['phone']}.")
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
