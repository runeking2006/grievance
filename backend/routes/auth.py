from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.database.connection import get_session
from backend.schemas.grievance import TokenRequest, TokenResponse, UserRegister, UserResponse
from backend.services.auth import (
    authenticate_api_key,
    create_access_token,
    get_optional_user,
    register_user,
)


router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=UserResponse)
def create_user(data: UserRegister, db: Session = Depends(get_session)) -> UserResponse:
    user, api_key = register_user(db, data.email, data.full_name)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        api_key=api_key,
    )


@router.post("/auth/token", response_model=TokenResponse)
def create_token(data: TokenRequest, db: Session = Depends(get_session)) -> TokenResponse:
    user = authenticate_api_key(db, data.email, data.api_key)
    token, expires_in = create_access_token(user)
    return TokenResponse(access_token=token, expires_in=expires_in, role=user.role)


@router.get("/me", response_model=UserResponse)
def me(
    db: Session = Depends(get_session),
    user=Depends(get_optional_user),
) -> UserResponse:
    if user is None:
        return UserResponse(id="anonymous", email="anonymous", full_name="Anonymous", role="anonymous", api_key=None)
    return UserResponse(id=user.id, email=user.email, full_name=user.full_name, role=user.role, api_key=None)
