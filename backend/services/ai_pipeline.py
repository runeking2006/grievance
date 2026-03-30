from backend.services.classifier import classify_complaint
from backend.services.urgency import detect_urgency
from backend.services.similarity import generate_embedding
from backend.utils.translator import translate


def process(text: str) -> dict:
    translated_text, language = translate(text)
    category = classify_complaint(translated_text)

    embedding = generate_embedding(translated_text)

    return {
        "category": category,
        "urgency": detect_urgency(translated_text),
        "embedding": embedding,
        "translated_text": translated_text,
        "language": language,
        "similar_complaints": [],
        "insight": "No similar issues found",
    }
