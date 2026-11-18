
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.config import settings
import secrets


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/demo-account")
def create_demo_account(db: Session = Depends(get_db)):
    if not settings.demo_mode:
        raise HTTPException(404, "Demo mode is disabled")
    for _ in range(3):
        # EmailStr rejects .local as a special-use domain during login.
        # example.com is reserved for examples and passes normal validation.
        email = f"demo-{secrets.token_hex(5)}@example.com"
        if db.scalar(select(User).where(User.email == email)) is None:
            password = secrets.token_urlsafe(18)
            user = User(email=email, password_hash=hash_password(password))
            db.add(user)
            db.commit()
            return {"email": email, "password": password}
    raise HTTPException(503, "Could not create a demo account. Please try again.")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    existing = db.scalar(
        select(User).where(User.email == email)
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    return user


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    email = str(payload.email).strip().lower()

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if (
        user is None
        or not verify_password(payload.password, user.password_hash)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
