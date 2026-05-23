# 100:0 LAB — Server

100:0 LAB의 백엔드 서버예요.
영상 업로드, 과실 투표, 사건 상태 추적, AI 자연어 검색, 사고 위치 geocoding을 처리해요.

---

## 시작하기

```bash
uv sync
uv run uvicorn app.main:app --reload
# → http://localhost:8000
```

환경 변수는 `.env` 파일로 관리해요 (`python-decouple`).

**시드 데이터가 필요하다면**

```bash
.venv/bin/python seed.py         # 영상, 태그, 투표, 사건 상태
.venv/bin/python index_all.py    # 벡터 임베딩 인덱싱
```

---

## 구조

```
app/
  api/v1/endpoints/   라우터 (video, vote, tag, case_status, comment, auth, user)
  models/             SQLAlchemy 모델
  schemas/            Pydantic 스키마
  services/           비즈니스 로직 (embedding, geocoding 등)
  db/                 DB 세션 + Base
```

---

## 스택

- **FastAPI** + **SQLAlchemy** (sync) + **SQLite**
- **sentence-transformers** — `jhgan/ko-sroberta-multitask` (한국어 벡터 검색)
- **Nominatim** — 주소 → 좌표 geocoding
- **Google OAuth** + **PyJWT** — 인증
- **uv** — 패키지 매니저
