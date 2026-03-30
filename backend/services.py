import re
from typing import Tuple
from models import Grievance

# Optional translator (safe fallback)
try:
    from googletrans import Translator
    _translator = Translator()
except:
    _translator = None


def translate_to_english(text: str) -> Tuple[str, str]:
    """Lightweight translation with fallback"""
    if not _translator:
        return text, "en"

    try:
        detection = _translator.detect(text)
        lang = detection.lang

        if lang != "en":
            translated = _translator.translate(text, dest="en")
            return translated.text, lang

        return text, "en"

    except Exception as e:
        print("Translation error:", e)
        return text, "en"


# 🔥 RULE-BASED CLASSIFICATION (FAST + ZERO MEMORY)
def classify_category(text: str) -> str:
    text = text.lower()

    # 🔥 PRIORITY FIRST (more specific)
    if any(word in text for word in ["wifi", "internet", "portal", "login", "server"]):
        return "IT"

    if any(word in text for word in ["fee", "payment", "tuition", "scholarship"]):
        return "Fees"

    if any(word in text for word in ["exam", "class", "faculty", "marks"]):
        return "Academic"

    if any(word in text for word in ["bus", "transport", "route", "driver"]):
        return "Transport"

    if any(word in text for word in ["hostel", "room", "mess", "warden"]):
        return "Hostel"

    return "General"


def detect_urgency(text: str) -> str:
    text = text.lower()

    if any(word in text for word in ["urgent", "immediately", "emergency", "critical", "danger"]):
        return "High"

    if any(word in text for word in ["soon", "important", "issue", "problem"]):
        return "Medium"

    return "Low"


def get_department(category: str) -> str:
    mapping = {
        "Hostel": "Hostel Office",
        "Fees": "Accounts Department",
        "IT": "IT Support",
        "Academic": "Dean's Office",
        "Transport": "Transport Manager",
        "General": "Administration"
    }

    return mapping.get(category, "Administration")


def process_grievance(complaint_text: str) -> Grievance:
    translated_text, lang = translate_to_english(complaint_text)
    category = classify_category(translated_text)
    urgency = detect_urgency(translated_text)
    department = get_department(category)

    return Grievance(
        complaint_text=complaint_text,
        translated_text=translated_text,
        category=category,
        urgency=urgency,
        department=department,
        language=lang
    )