from pydantic import BaseModel


class GoogleAuthRequest(BaseModel):
    code: str


class KakaoAuthRequest(BaseModel):
    access_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
