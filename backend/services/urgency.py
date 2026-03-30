def detect_urgency(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["urgent", "immediately", "emergency", "critical", "danger"]):
        return "High"
    if any(word in lowered for word in ["soon", "important", "issue", "problem"]):
        return "Medium"
    return "Low"
