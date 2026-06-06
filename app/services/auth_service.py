import os
import jwt
import requests
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.token import Token
from app.schemas.user import UserCreate
from app.services import email_service
from settings import (
    GOOGLE_TOKEN_INFO_URL,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

def _env(key: str, default: str = "") -> str:
    return os.getenv(key) or default

JWT_SECRET_KEY = _env("JWT_SECRET_KEY", "dev-secret-key")
JWT_ALGORITHM = _env("JWT_ALGORITHM", "HS256")


def _create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _get_or_create_user(db: Session, user_data: UserCreate) -> User:
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        user = User(
            email=user_data.email,
            nickname=user_data.nickname,
            profile_image=user_data.profile_image,
            user_type=user_data.user_type,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        try:
            email_service.send_admin_new_user(user.email, user.nickname or "")
        except Exception:
            pass
    return user


def _issue_tokens(db: Session, user: User) -> dict:
    access_token = _create_token(
        {"sub": user.email, "user_id": user.id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = _create_token(
        {"sub": user.email, "user_id": user.id},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    token_obj = db.query(Token).filter(Token.user_id == user.id).first()
    if token_obj:
        token_obj.refresh_token = refresh_token
        token_obj.is_active = True
    else:
        db.add(Token(user_id=user.id, refresh_token=refresh_token, is_active=True))
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token}


def google_auth(code: str, db: Session) -> dict:
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": _env("GOOGLE_CLIENT_ID"),
            "client_secret": _env("GOOGLE_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": _env("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback/google"),
        },
    )
    token_json = token_res.json()
    if "access_token" not in token_json:
        print("Google token error:", token_json)
        raise HTTPException(status_code=400, detail=token_json.get("error_description", "Google 토큰 발급 실패"))

    user_res = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {token_json['access_token']}"},
    )
    user_info = user_res.json()
    if "email" not in user_info:
        raise HTTPException(status_code=400, detail="Google 사용자 정보 조회 실패")

    user = _get_or_create_user(
        db,
        UserCreate(
            email=user_info["email"],
            nickname=user_info.get("name"),
            profile_image=user_info.get("picture"),
            user_type=1,
        ),
    )
    tokens = _issue_tokens(db, user)
    return {"user": {"id": user.id, "email": user.email, "nickname": user.nickname}, **tokens}


def kakao_auth(access_token: str, db: Session) -> dict:
    user_res = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if user_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Kakao 사용자 정보 조회 실패")

    user_info = user_res.json()
    kakao_account = user_info.get("kakao_account", {})
    email = kakao_account.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Kakao 이메일 정보 없음")

    profile = kakao_account.get("profile", {})
    user = _get_or_create_user(
        db,
        UserCreate(
            email=email,
            nickname=profile.get("nickname"),
            profile_image=profile.get("profile_image_url"),
            user_type=2,
        ),
    )
    tokens = _issue_tokens(db, user)
    return {"user": {"id": user.id, "email": user.email, "nickname": user.nickname}, **tokens}


def refresh_tokens(refresh_token: str, db: Session) -> dict:
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token 만료")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 refresh token")

    user_id = payload.get("user_id")
    email = payload.get("sub")

    token_obj = db.query(Token).filter(
        Token.user_id == user_id,
        Token.refresh_token == refresh_token,
        Token.is_active == True,
    ).first()

    if not token_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 refresh token")

    user = db.query(User).filter(User.id == user_id).first()
    return _issue_tokens(db, user)


def logout(user_id: int, db: Session):
    tokens = db.query(Token).filter(Token.user_id == user_id).all()
    for token in tokens:
        token.is_active = False
    db.commit()
