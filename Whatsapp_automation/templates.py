"""Message templates with {placeholders}, chosen by contact tag."""

PROMO = """Dear {name},
Thank you for visiting the Vikram Hospitals – Free Health Screening Camp, conducted in partnership with TejAI Services.
మీరు విక్రమ్ హాస్పిటల్స్, గుంటూరు వారి తోట, గుంటూరులో నిర్వహించిన ఉచిత ఆరోగ్య పరీక్షా శిబిరానికి హాజరైనందుకు ధన్యవాదాలు.
🩺 Your Screening Results | మీ ఆరోగ్య పరీక్షల వివరాలు
BMI: 27.4 kg/m²
BMI Category: Overweight
BMI వర్గం: అధిక బరువు
Blood Sugar: 118 mg/dL
Test: Random
బ్లడ్ షుగర్: 118 mg/dL
పరీక్ష: రాండమ్
Blood Pressure: 128/82 mmHg
బ్లడ్ ప్రెషర్: 128/82 mmHg
🥗 FREE Nutritionist Consultation | ఉచిత న్యూట్రిషనిస్ట్ సంప్రదింపు
As a participant of the camp, you are eligible for ONE FREE consultation with our Nutritionist.
ఈ క్యాంప్‌లో పాల్గొన్నందుకు న్యూట్రిషనిస్ట్‌తో ఒక ఉచిత సంప్రదింపు అవకాశం మీకు ఉంది.
👉 Interested? Reply “YES” to this WhatsApp message to book your FREE consultation.
👉 ఆసక్తి ఉంటే, మీ ఉచిత సంప్రదింపును బుక్ చేసుకోవడానికి ఈ WhatsApp మెసేజ్‌కు “YES” అని రిప్లై చేయండి.
⚠️ Important | ముఖ్యమైన సమాచారం
These are screening results for health awareness and do not constitute a medical diagnosis. Please consult a qualified doctor if you have concerns about your results.
ఇవి ఆరోగ్య అవగాహన కోసం నిర్వహించిన స్క్రీనింగ్ పరీక్షల ఫలితాలు మాత్రమే. ఇవి వైద్య నిర్ధారణ కావు. మీ ఫలితాలపై ఏవైనా సందేహాలు ఉంటే, అర్హత కలిగిన వైద్యులను సంప్రదించండి.
📞 Contact | సంప్రదించండి: 70757 20062
Vikram Hospitals
Guntur Vari Thota, Guntur"""

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