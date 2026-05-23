from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.security import get_current_user
from app.schemas.auth import GoogleAuthRequest, KakaoAuthRequest, RefreshTokenRequest
from app.services.auth_service import google_auth, kakao_auth, refresh_tokens, logout

router = APIRouter()


@router.post("/google")
def google_login(body: GoogleAuthRequest, db: Session = Depends(get_db)):
    return google_auth(body.code, db)


@router.post("/kakao")
def kakao_login(body: KakaoAuthRequest, db: Session = Depends(get_db)):
    return kakao_auth(body.access_token, db)


@router.post("/refresh")
def refresh(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    return refresh_tokens(body.refresh_token, db)


@router.post("/logout")
def logout_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    logout(user_id, db)
    return JSONResponse(content={"message": "로그아웃 완료"}, status_code=200)


@router.get("/me")
def me(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    return {"id": user.id, "email": user.email, "nickname": user.nickname, "profile_image": user.profile_image}
