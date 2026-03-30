from threading import Lock

from backend.config.settings import settings


_generator = None
_generator_lock = Lock()


def _load_generator():
    global _generator

    if _generator is not None:
        return _generator

    with _generator_lock:
        if _generator is not None:
            return _generator

        if not settings.GENERATOR_ENABLED:
            return None

        try:
            from transformers import pipeline

            _generator = pipeline(
                task="text2text-generation",
                model=settings.GENERATOR_MODEL,
            )
        except Exception:
            _generator = None

    return _generator


def warmup_generator() -> None:
    _load_generator()


def _fallback_insight(category: str, similar_complaints: list[str]) -> str:
    count = len(similar_complaints)
    if count >= 3:
        return f"Frequent issue detected in {category} based on multiple related complaints."
    if count > 0:
        return f"Related complaints were retrieved for {category}; this may indicate an emerging issue."
    return "No similar issues found"


def generate_rag_insight(
    complaint_text: str,
    category: str,
    similar_complaints: list[str],
    urgency: str | None = None,
    department: str | None = None,
    location: str | None = None,
) -> str:
    if not similar_complaints:
        return "No similar issues found"

    generator = _load_generator()
    if generator is None:
        return _fallback_insight(category, similar_complaints)

    context = "\n".join(f"- {item}" for item in similar_complaints)
    prompt = (
        "You are a campus grievance analyst writing short operational insights for an admin dashboard. "
        "Use the retrieved complaints as evidence. "
        "Mention recurrence or impact only if supported by the retrieved context. "
        f"Category: {category}. "
        f"Urgency: {urgency or 'Unknown'}. "
        f"Department: {department or 'Unknown'}. "
        f"Location: {location or 'Unknown'}. "
        f"Current complaint: {complaint_text}. "
        f"Retrieved complaints:\n{context}\n"
        "Return one concise sentence for operations staff."
    )

    try:
        result = generator(
            prompt,
            max_new_tokens=40,
            do_sample=False,
        )
        generated_text = result[0]["generated_text"].strip()
        return generated_text or _fallback_insight(category, similar_complaints)
    except Exception:
        return _fallback_insight(category, similar_complaints)
