# 100:0 연구소 — 백엔드 서버 스펙

## 개요

블랙박스 사고 영상 플랫폼 **100:0 연구소**의 백엔드 서버.
FastAPI + SQLite 기반, JWT 인증, 벡터 검색, geocoding 기능 포함.

---

## 기술 스택

| 구분 | 스택 |
|------|------|
| 프레임워크 | FastAPI |
| ORM | SQLAlchemy (sync) |
| DB | SQLite (`app/db/mib.db`) |
| 마이그레이션 | Alembic |
| 인증 | Google OAuth + JWT (PyJWT) |
| 벡터 검색 | sentence-transformers `jhgan/ko-sroberta-multitask` (768차원) |
| Geocoding | OpenStreetMap Nominatim |
| 패키지 관리 | uv (`/Users/aepeul/.local/bin/uv`) |

---

## 경로

- **서버 루트**: `/Users/aepeul/dev/server/100-0-lab-server`
- **DB**: `app/db/mib.db` (실사용), `mnm.db`는 구버전 미사용
- **venv**: `.venv/bin/python` (activate 안 먹힘, 직접 경로 사용)

---

## 디렉토리 구조

```
app/
├── api/v1/
│   ├── api.py              # 라우터 등록
│   └── endpoints/
│       ├── auth.py
│       ├── user.py
│       ├── video.py
│       ├── vote.py
│       ├── tag.py
│       ├── case_status.py
│       └── comment.py
├── db/
│   ├── base.py             # Base, id/created_at/updated_at 자동 포함
│   ├── session.py          # get_db()
│   └── mib.db              # 실사용 DB
├── models/
│   ├── user.py
│   ├── video.py
│   ├── vote.py
│   ├── tag.py
│   ├── case_status.py
│   ├── video_embedding.py
│   ├── token.py
│   └── comment.py
├── schemas/
│   ├── auth.py
│   ├── user.py
│   ├── video.py
│   ├── search.py
│   ├── vote.py
│   ├── tag.py
│   ├── case_status.py
│   └── comment.py
├── services/
│   ├── auth_service.py
│   ├── video_service.py
│   ├── embedding_service.py
│   ├── geocoding_service.py
│   ├── vote_service.py
│   ├── tag_service.py
│   ├── case_status_service.py
│   ├── comment_service.py
│   └── user_service.py
└── main.py
alembic/
seed.py
```

---

## 데이터베이스 모델

### Base (공통)
모든 모델에 자동 포함: `id`, `created_at`, `updated_at`

### User
```python
email         # unique, indexed
nickname
profile_image
user_type     # 0: 일반, 1: Google, 2: Kakao
is_deleted
# Relationships: videos, tokens, comments
```

### Video
```python
user_id       # FK → User
title
description
video_url
thumbnail_url
views         # default: 0
filmed_date   # Date, nullable
filmed_location
# Relationships: user, tags, embedding, comments
```

### Vote
```python
video_id      # FK
user_id       # FK
ratio         # "100:0" | "80:20" | "70:30" | "60:40" | "50:50" | "0:100"
# UniqueConstraint: (video_id, user_id)
```

### Tag
```python
video_id      # FK
name
# UniqueConstraint: (video_id, name)
# Relationship: video (back_populates="tags")
```

### CaseStatus
```python
video_id        # FK, unique
status          # 9단계 (아래 참고)
updated_by      # FK → User
actual_ratio    # nullable — 공식 과실 비율 (Result Reveal)
resolution_note # nullable — 결론 메모
```
**status 단계**: 접수됨 → 보험사 접수 → 경찰 조사 중 → 합의 진행 중 → 소송 진행 중 → 1심 판결 → 항소 중 → 최종 판결 → 종결

### VideoEmbedding
```python
video_id    # FK, unique
embedding   # LargeBinary — pickle.dumps(numpy array, 768차원)
```

### Comment
```python
video_id        # FK, indexed, ondelete="CASCADE"
user_id         # FK, ondelete="CASCADE"
content
is_party        # bool, default False
party_role      # nullable: "가해자" | "피해자" | "목격자"
party_verified  # bool — 업로더가 인증
```

### Token
```python
refresh_token
user_id       # FK
is_active     # bool, default True
```

---

## API 엔드포인트

### Auth — `POST /api/v1/auth/`
```
POST /google              # Google OAuth 로그인
POST /kakao               # Kakao OAuth 로그인
POST /refresh             # 토큰 갱신
POST /logout              # 로그아웃
GET  /me                  # 현재 사용자 정보
```

### Users — `/api/v1/users/`
```
GET /me
GET /{user_id}
GET /{user_id}/videos
```

### Videos — `/api/v1/videos/`
```
GET  /feed?cursor=X               # 무한스크롤 피드
GET  /search?q=X&top_k=10        # 벡터 검색
GET  /locations                   # geocoding 위치 목록
GET  /top?limit=10                # 인기 영상 TOP N
GET  /controversial?limit=10      # 논란 영상 (투표 팽팽)
GET  /{id}/related                # 연관 영상 (벡터 유사도)
GET  /{id}                        # 영상 상세
POST /upload                      # 영상 업로드 (FormData)
DELETE /{id}                      # 영상 삭제
```
> ⚠️ `/feed`, `/search`, `/locations`, `/top`, `/controversial`은 `/{video_id}` 앞에 등록 필수

### Votes — `/api/v1/videos/`
```
POST /{id}/votes
GET  /{id}/votes
GET  /{id}/votes/me
```

### Tags — `/api/v1/videos/`
```
GET    /{id}/tags
POST   /{id}/tags
DELETE /{id}/tags/{tag_id}
```

### Case Status — `/api/v1/videos/`
```
GET /{id}/case-status
PUT /{id}/case-status     # 업로더만 가능
```

### Comments — `/api/v1/videos/`
```
GET    /{id}/comments
POST   /{id}/comments
DELETE /comments/{comment_id}
POST   /{id}/comments/{comment_id}/verify-party   # 업로더가 당사자 인증
```

---

## 서비스 레이어

| 서비스 | 역할 |
|--------|------|
| `auth_service` | Google/Kakao OAuth, JWT 발급/갱신 |
| `video_service` | 피드, 업로드, TOP/논란/연관 영상 |
| `embedding_service` | 벡터 임베딩, 코사인 유사도 검색, 인메모리 캐시 |
| `geocoding_service` | Nominatim 주소→좌표, 메모리 캐시 |
| `vote_service` | 투표 등록/집계 |
| `tag_service` | 태그 CRUD |
| `case_status_service` | 사건 진행 상태 관리 |
| `comment_service` | 댓글 CRUD, 당사자 인증 |
| `user_service` | 사용자 정보 조회 |

---

## 벡터 검색 파이프라인

```
1. 영상 업로드 → index_video(video_id, db) 호출
2. 제목 + 설명 + 태그 → corpus 텍스트 빌드
3. jhgan/ko-sroberta-multitask → 768차원 numpy array
4. pickle.dumps() → VideoEmbedding.embedding (BLOB)
5. 서버 시작 시 load_cache() → _cache: dict[int, np.ndarray]
6. 검색: 쿼리 임베딩 → 코사인 유사도 → top_k 반환
```

---

## 인증 흐름

```
1. Google OAuth code → POST /auth/google
2. JWT access_token + refresh_token 발급
3. 클라이언트: localStorage 저장
4. API 요청: Authorization: Bearer {access_token}
5. 만료 시: POST /auth/refresh { refresh_token }
```

---

## 개발 명령어

```bash
# 서버 실행
.venv/bin/uvicorn app.main:app --reload

# 패키지 설치
/Users/aepeul/.local/bin/uv add <package>

# 마이그레이션
.venv/bin/alembic upgrade head

# 시드 데이터 (영상 12개, 태그 36개, 투표, 사건상태)
.venv/bin/python seed.py

# 임베딩 재인덱싱 (마이그레이션 후 필요)
.venv/bin/python scripts/index_all.py
```

---

## 주의사항

- `source .venv/bin/activate` 안 먹힘 → `.venv/bin/python` 직접 사용
- pip 없음 → `uv add`로 패키지 설치
- DB는 `mib.db`만 사용 (`mnm.db` 구버전, 삭제됨)
- 마이그레이션 후 기존 데이터 임베딩 재인덱싱 필요
- 패턴: `model → schema → service → endpoint`
