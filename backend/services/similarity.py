import hashlib
import math

from backend.config.settings import settings

VECTOR_SIZE = settings.VECTOR_DIMENSION


def _hashed_embedding(text: str) -> list[float]:
    vector = [0.0] * VECTOR_SIZE
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for index in range(VECTOR_SIZE):
            vector[index] += digest[index % len(digest)] / 255.0
    return vector


def generate_embedding(text: str) -> list[float]:
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except ImportError:
        return _hashed_embedding(text)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    return list(model.encode(text, normalize_embeddings=True))


def cosine_similarity_score(first: list[float], second: list[float]) -> float:
    if not first or not second or len(first) != len(second):
        return 0.0

    numerator = sum(a * b for a, b in zip(first, second))
    left = math.sqrt(sum(a * a for a in first))
    right = math.sqrt(sum(b * b for b in second))
    if left == 0.0 or right == 0.0:
        return 0.0
    return numerator / (left * right)


def find_similar(
    new_embedding: list[float],
    stored_embeddings: list[list[float]],
    stored_texts: list[str],
    threshold: float = 0.75,
) -> list[str]:
    if not stored_embeddings or not stored_texts:
        return []

    matches: list[str] = []
    for index, embedding in enumerate(stored_embeddings):
        if cosine_similarity_score(new_embedding, embedding) > threshold:
            matches.append(stored_texts[index])

    unique_matches: list[str] = []
    seen: set[str] = set()
    for text in matches:
        if text not in seen:
            unique_matches.append(text)
            seen.add(text)

    return unique_matches[:3]
