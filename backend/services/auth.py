import hashlib
import hmac
import json
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from backend.config.settings import settings
from backend.database.connection import get_session
from backend.models.user import UserAccount


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _b64encode(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode(value + padding)


def _jwt_sign(message: bytes) -> str:
    digest = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256,
    ).digest()
    return _b64encode(digest)


def create_access_token(user: UserAccount) -> tuple[str, int]:
    expires_in = settings.JWT_EXPIRE_MINUTES * 60
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "exp": int((datetime.now(timezone.utc) + timedelta(seconds=expires_in)).timestamp()),
    }
    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    message = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = _jwt_sign(message)
    return f"{header_b64}.{payload_b64}.{signature}", expires_in


def decode_access_token(token: str) -> dict:
    try:
        header_b64, payload_b64, signature = token.split(".")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token format") from exc

    message = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected = _jwt_sign(message)
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid token signature")

    payload = json.loads(_b64decode(payload_b64))
    if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="Token expired")
    return payload


def register_user(
    db: Session,
    email: str,
    full_name: str | None = None,
    role: str | None = None,
) -> tuple[UserAccount, str]:
    existing = db.exec(select(UserAccount).where(UserAccount.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    api_key = secrets.token_urlsafe(32)
    user = UserAccount(
        id=str(uuid4()),
        email=email,
        full_name=full_name,
        api_key_hash=hash_api_key(api_key),
        role=role or settings.USER_DEFAULT_ROLE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, api_key


def get_user_by_api_key(db: Session, api_key: str) -> UserAccount | None:
    return db.exec(
        select(UserAccount).where(UserAccount.api_key_hash == hash_api_key(api_key))
    ).first()


def get_user_by_id(db: Session, user_id: str) -> UserAccount | None:
    return db.get(UserAccount, user_id)


def authenticate_api_key(db: Session, email: str, api_key: str) -> UserAccount:
    user = db.exec(select(UserAccount).where(UserAccount.email == email)).first()
    if user is None or user.api_key_hash != hash_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")
    return user


def _extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str | None:
    if credentials is None:
        return None
    if credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return credentials.credentials


def get_api_key(x_api_key: str | None = Depends(api_key_header)) -> str | None:
    return x_api_key


def require_user(
    db: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_api_key: str | None = Depends(get_api_key),
) -> UserAccount:
    token = _extract_bearer_token(credentials)
    if token:
        payload = decode_access_token(token)
        user = get_user_by_id(db, payload["sub"])
    elif x_api_key:
        user = get_user_by_api_key(db, x_api_key)
    else:
        raise HTTPException(status_code=401, detail="Authentication required")
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user


def get_optional_user(
    db: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_api_key: str | None = Depends(get_api_key),
) -> UserAccount | None:
    token = _extract_bearer_token(credentials)
    if token:
        payload = decode_access_token(token)
        user = get_user_by_id(db, payload["sub"])
    elif x_api_key:
        user = get_user_by_api_key(db, x_api_key)
    else:
        return None
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user


def require_roles(*roles: str):
    def _dependency(user: UserAccount = Depends(require_user)) -> UserAccount:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return _dependency
