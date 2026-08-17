"""
POST /auth/signup, POST /auth/login, GET /auth/me.

Fully additive: this router is registered in app/main.py alongside the
existing router, but nothing here is imported by — or required by — the
upload/job/export code. Auth does not currently gate any existing route.
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .db import get_db
from .schemas import LoginRequest, SignupRequest, TokenResponse, UserResponse
from .security import create_access_token, decode_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_email(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    if credentials is None:
        raise HTTPException(401, "Not authenticated.")
    email = decode_access_token(credentials.credentials)
    if email is None:
        raise HTTPException(401, "Invalid or expired token.")
    return email


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(body: SignupRequest):
    hashed = hash_password(body.password)
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
                (body.email.lower(), hashed),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account with this email already exists.")

    token = create_access_token(body.email.lower())
    return TokenResponse(access_token=token, email=body.email.lower())


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    with get_db() as conn:
        row = conn.execute(
            "SELECT hashed_password FROM users WHERE email = ?", (body.email.lower(),)
        ).fetchone()

    if row is None or not verify_password(body.password, row["hashed_password"]):
        raise HTTPException(401, "Incorrect email or password.")

    token = create_access_token(body.email.lower())
    return TokenResponse(access_token=token, email=body.email.lower())


@router.get("/me", response_model=UserResponse)
def me(email: str = Depends(get_current_user_email)):
    return UserResponse(email=email)
