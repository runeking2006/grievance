from threading import Lock

from backend.config.settings import settings


CATEGORY_PROMPTS = {
    "Hostel": "hostel facilities and accommodation",
    "Fees": "fees, scholarships, accounts, or payments",
    "IT": "internet, wifi, portals, or technical support",
    "Academic": "classes, exams, faculty, or marks",
    "Transport": "buses, routes, or transportation",
    "General": "general administration or other campus issues",
}

_classifier = None
_classifier_lock = Lock()


def _fallback_classify(text: str) -> str:
    lowered = text.lower()

    if any(word in lowered for word in ["wifi", "internet", "portal", "login", "server"]):
        return "IT"
    if any(word in lowered for word in ["fee", "payment", "tuition", "scholarship"]):
        return "Fees"
    if any(word in lowered for word in ["exam", "class", "faculty", "marks"]):
        return "Academic"
    if any(word in lowered for word in ["bus", "transport", "route", "driver"]):
        return "Transport"
    if any(word in lowered for word in ["hostel", "room", "mess", "warden", "water"]):
        return "Hostel"
    return "General"


def _load_classifier():
    global _classifier

    if _classifier is not None:
        return _classifier

    with _classifier_lock:
        if _classifier is not None:
            return _classifier

        if not settings.CLASSIFIER_ENABLED:
            return None

        try:
            from transformers import pipeline

            _classifier = pipeline(
                task="zero-shot-classification",
                model=settings.CLASSIFIER_MODEL,
            )
        except Exception:
            _classifier = None

    return _classifier


def warmup_classifier() -> None:
    _load_classifier()


def classify_complaint(text: str) -> str:
    classifier = _load_classifier()
    if classifier is None:
        return _fallback_classify(text)

    try:
        result = classifier(
            text,
            list(CATEGORY_PROMPTS.values()),
            hypothesis_template="This complaint is about {}.",
            multi_label=False,
        )
    except Exception:
        return _fallback_classify(text)

    top_label = result["labels"][0]
    for category, prompt in CATEGORY_PROMPTS.items():
        if prompt == top_label:
            return category

    return _fallback_classify(text)
