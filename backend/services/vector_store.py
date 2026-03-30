from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlmodel import Session

from backend.config.settings import settings


def is_postgres_engine(engine: Engine) -> bool:
    return engine.url.get_backend_name().startswith("postgresql")


def embedding_to_vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def ensure_vector_schema(engine: Engine) -> None:
    if not settings.PGVECTOR_ENABLED or not is_postgres_engine(engine):
        return

    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            columns = {column["name"] for column in inspect(engine).get_columns("grievance")}
            if "embedding_vector" not in columns:
                connection.execute(
                    text(
                        f"ALTER TABLE grievance ADD COLUMN embedding_vector vector({settings.VECTOR_DIMENSION})"
                    )
                )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_grievance_embedding_vector "
                    "ON grievance USING hnsw (embedding_vector vector_cosine_ops) "
                    "WITH (m = 16, ef_construction = 64)"
                )
            )
    except Exception:
        return


def save_vector_embedding(session: Session, grievance_id: int, embedding: list[float]) -> None:
    if not settings.PGVECTOR_ENABLED or not is_postgres_engine(session.bind):
        return

    try:
        session.execute(
            text(
                "UPDATE grievance "
                "SET embedding_vector = CAST(:embedding AS vector) "
                "WHERE id = :grievance_id"
            ),
            {
                "embedding": embedding_to_vector_literal(embedding),
                "grievance_id": grievance_id,
            },
        )
    except Exception:
        return


def vector_similar_texts(
    session: Session,
    embedding: list[float],
    category: str | None,
    location: str | None,
    limit: int,
) -> list[str] | None:
    if not settings.PGVECTOR_ENABLED or not is_postgres_engine(session.bind):
        return None

    clauses = ["embedding_vector IS NOT NULL"]
    params: dict[str, object] = {
        "embedding": embedding_to_vector_literal(embedding),
        "limit": limit,
    }
    if category:
        clauses.append("category = :category")
        params["category"] = category
    if location:
        clauses.append("(location = :location OR location IS NULL)")
        params["location"] = location

    query = text(
        "SELECT complaint_text, embedding_vector <=> CAST(:embedding AS vector) AS distance "
        "FROM grievance "
        f"WHERE {' AND '.join(clauses)} "
        "ORDER BY embedding_vector <=> CAST(:embedding AS vector) "
        "LIMIT :limit"
    )
    try:
        session.execute(text(f"SET LOCAL hnsw.ef_search = {settings.VECTOR_HNSW_EF_SEARCH}"))
        result = session.execute(query, params).all()
    except Exception:
        return None
    return [row[0] for row in result if row[1] <= settings.VECTOR_SIMILARITY_THRESHOLD]
