"""
Mock 데이터 시드 스크립트
실행: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.video import Video
from app.models.vote import Vote
from app.models.tag import Tag
from app.models.case_status import CaseStatus

DATABASE_URL = "sqlite:///./app/db/mib.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
db = Session()

# ── 기존 seed 데이터 정리 ──────────────────────────────────────────
print("기존 seed 데이터 정리 중...")
db.query(CaseStatus).delete()
db.query(Tag).delete()
db.query(Vote).delete()
db.query(Video).delete()
db.query(User).filter(User.email.like("seed_%")).delete()
db.commit()

# ── 유저 생성 ────────────────────────────────────────────────────
print("유저 생성 중...")
users = []
user_data = [
    ("seed_user1@test.com", "블박러_김씨", 1),
    ("seed_user2@test.com", "억울한_이씨", 1),
    ("seed_user3@test.com", "보험왕_박씨", 1),
    ("seed_user4@test.com", "사고목격자", 1),
    ("seed_user5@test.com", "블박채널", 1),
]
for email, nickname, user_type in user_data:
    u = User(email=email, nickname=nickname, user_type=user_type)
    db.add(u)
    users.append(u)
db.commit()
for u in users:
    db.refresh(u)

# ── 영상 생성 ────────────────────────────────────────────────────
print("영상 생성 중...")
videos_data = [
    {
        "user_idx": 0,
        "title": "[블박] 무단횡단 보행자와 충돌 — 과실 100:0 맞나요?",
        "description": "신호 지키고 직진하던 중 갑자기 뛰어든 보행자와 충돌했습니다.\n보험사에서는 제 과실이 일부 있다고 하는데 납득이 안 됩니다.\n영상 보시고 판단 부탁드립니다.",
        "filmed_date": date(2025, 11, 3),
        "filmed_location": "서울 강남구 테헤란로",
        "views": 48200,
    },
    {
        "user_idx": 1,
        "title": "끼어들기 차량에 추돌 — 보험처리 거부당함",
        "description": "고속도로 진입로에서 갑자기 끼어드는 차량 때문에 추돌사고가 났습니다.\n상대방이 블랙박스 영상이 없다며 50:50 주장 중입니다.",
        "filmed_date": date(2025, 12, 17),
        "filmed_location": "경부고속도로 서울요금소 부근",
        "views": 31500,
    },
    {
        "user_idx": 2,
        "title": "신호위반 차량 측면 추돌 — 현재 재판 진행 중",
        "description": "빨간불에 정지해 있던 중 신호위반 차량이 측면을 들이받았습니다.\n형사 처벌 원해서 현재 재판 중입니다. 진행 상황 공유합니다.",
        "filmed_date": date(2025, 10, 5),
        "filmed_location": "인천시 남동구 논현동 사거리",
        "views": 92100,
    },
    {
        "user_idx": 3,
        "title": "주차장에서 내 차 긁고 도망간 차량 — CCTV 없음",
        "description": "대형마트 주차장에서 제 차를 긁고 그냥 간 차량입니다.\n블박에 찍힌 차량 번호로 신고했고 현재 경찰 조사 중입니다.",
        "filmed_date": date(2026, 1, 22),
        "filmed_location": "경기도 수원시 영통구",
        "views": 15700,
    },
    {
        "user_idx": 4,
        "title": "역주행 차량과 정면충돌 직전 — 아찔한 순간",
        "description": "편도 2차로 도로에서 역주행해오는 차량. 간신히 피했습니다.\n경찰에 신고했고 해당 차량 면허 취소 처분을 원합니다.",
        "filmed_date": date(2025, 9, 30),
        "filmed_location": "부산시 해운대구 해운대로",
        "views": 203000,
    },
    {
        "user_idx": 0,
        "title": "보복운전 후 칼치기 — 고의성 있음",
        "description": "앞차가 갑자기 브레이크를 밟더니 이후 계속 제 차 앞에서 급감속을 반복했습니다.\n명백한 보복운전으로 신고 완료했습니다.",
        "filmed_date": date(2026, 2, 8),
        "filmed_location": "서울 송파구 올림픽로",
        "views": 67800,
    },
    {
        "user_idx": 1,
        "title": "어린이보호구역 과속차량 — 아이 튀어나옴",
        "description": "스쿨존에서 시속 60km 이상으로 달리던 차량. 옆 골목에서 아이가 뛰어나왔는데 간발의 차이로 사고를 피했습니다.",
        "filmed_date": date(2026, 1, 9),
        "filmed_location": "경기도 고양시 덕양구",
        "views": 145000,
    },
    {
        "user_idx": 2,
        "title": "우회전 중 직진 오토바이와 충돌 — 과실 비율 논쟁 중",
        "description": "우회전 신호에 천천히 우회전하던 중 직진하던 배달 오토바이와 충돌.\n보험사마다 과실 비율이 다르게 나와서 혼란스럽습니다.",
        "filmed_date": date(2025, 11, 28),
        "filmed_location": "서울 마포구 홍대입구역 앞",
        "views": 38900,
    },
    {
        "user_idx": 3,
        "title": "음주운전 차량에 후방 추돌 — 상대 음주 적발",
        "description": "정차 중 뒤에서 들이받혔는데 상대 운전자가 술을 마신 상태였습니다.\n현재 형사 고소와 민사 손해배상 동시 진행 중입니다.",
        "filmed_date": date(2025, 8, 15),
        "filmed_location": "서울 영등포구 여의대방로",
        "views": 178000,
    },
    {
        "user_idx": 4,
        "title": "차선 변경 중 접촉사고 — 제가 잘못한 건가요?",
        "description": "방향지시등 켜고 차선 변경하던 중 접촉. 상대방이 블랙박스가 없어서 제 과실이라고 주장합니다.",
        "filmed_date": date(2026, 2, 14),
        "filmed_location": "경기도 성남시 분당구",
        "views": 9400,
    },
    {
        "user_idx": 0,
        "title": "중앙선 침범 차량 — 합의 완료 후기",
        "description": "중앙선 침범 차량과 정면충돌. 상대방 100% 과실 인정받고 합의 완료했습니다.\n과정 공유합니다.",
        "filmed_date": date(2025, 7, 4),
        "filmed_location": "강원도 춘천시 의암호반로",
        "views": 55300,
    },
    {
        "user_idx": 1,
        "title": "비 오는 날 미끄러진 차량과 충돌 — 천재지변?",
        "description": "빗길에 미끄러진 차량이 제 차를 들이받았습니다. 상대방이 천재지변이라고 주장하는데 가능한가요?",
        "filmed_date": date(2025, 6, 22),
        "filmed_location": "서울 서초구 반포대로",
        "views": 22100,
    },
]

videos = []
for d in videos_data:
    v = Video(
        user_id=users[d["user_idx"]].id,
        title=d["title"],
        description=d["description"],
        video_url="uploads/sample.mp4",
        thumbnail_url=None,
        filmed_date=d["filmed_date"],
        filmed_location=d["filmed_location"],
        views=d["views"],
    )
    db.add(v)
    videos.append(v)
db.commit()
for v in videos:
    db.refresh(v)

# ── 태그 ────────────────────────────────────────────────────────
print("태그 생성 중...")
tags_data = [
    (0, ["#보행자사고", "#무단횡단", "#과실분쟁"]),
    (1, ["#끼어들기", "#고속도로", "#보험거부"]),
    (2, ["#신호위반", "#측면충돌", "#재판중"]),
    (3, ["#주차사고", "#뺑소니", "#CCTV없음"]),
    (4, ["#역주행", "#정면충돌", "#면허취소"]),
    (5, ["#보복운전", "#칼치기", "#고의사고"]),
    (6, ["#스쿨존", "#어린이보호구역", "#과속"]),
    (7, ["#우회전", "#오토바이", "#과실비율"]),
    (8, ["#음주운전", "#후방추돌", "#형사고소"]),
    (9, ["#차선변경", "#접촉사고", "#블랙박스없음"]),
    (10, ["#중앙선침범", "#합의완료", "#100대0"]),
    (11, ["#빗길", "#미끄러짐", "#천재지변"]),
]
for video_idx, tag_names in tags_data:
    for name in tag_names:
        db.add(Tag(video_id=videos[video_idx].id, name=name))
db.commit()

# ── 사건 진행 상태 ───────────────────────────────────────────────
print("사건 진행 상태 생성 중...")
status_data = [
    (0, "보험사_협의중"),
    (1, "조사_진행중"),
    (2, "재판_진행중"),
    (3, "경찰_신고접수"),
    (4, "검찰_송치"),
    (5, "보험사_협의중"),
    (6, "경찰_신고접수"),
    (7, "보험사_협의중"),
    (8, "재판_진행중"),
    (9, "알_수_없음"),
    (10, "합의_완료"),
    (11, "보험_처리완료"),
]
for video_idx, status in status_data:
    db.add(CaseStatus(
        video_id=videos[video_idx].id,
        status=status,
        updated_by=videos[video_idx].user_id,
    ))
db.commit()

# ── 투표 ────────────────────────────────────────────────────────
print("투표 생성 중...")
import random
random.seed(42)

vote_distributions = [
    {0: ("100:0", 62), 1: ("90:10", 20), 2: ("80:20", 10), 3: ("70:30", 5), 4: ("60:40", 2), 5: ("50:50", 1)},  # 영상0: 명백히 보행자 잘못
    {0: ("100:0", 48), 1: ("90:10", 28), 2: ("80:20", 14), 3: ("70:30", 7), 4: ("60:40", 2), 5: ("50:50", 1)},  # 영상1: 끼어들기
    {0: ("100:0", 78), 1: ("90:10", 14), 2: ("80:20", 5), 3: ("70:30", 2), 4: ("60:40", 1), 5: ("50:50", 0)},   # 영상2: 신호위반
    {0: ("100:0", 85), 1: ("90:10", 10), 2: ("80:20", 3), 3: ("70:30", 1), 4: ("60:40", 1), 5: ("50:50", 0)},   # 영상3: 주차뺑소니
    {0: ("100:0", 91), 1: ("90:10", 7), 2: ("80:20", 1), 3: ("70:30", 1), 4: ("60:40", 0), 5: ("50:50", 0)},    # 영상4: 역주행
    {0: ("100:0", 73), 1: ("90:10", 18), 2: ("80:20", 6), 3: ("70:30", 2), 4: ("60:40", 1), 5: ("50:50", 0)},   # 영상5: 보복운전
    {0: ("100:0", 65), 1: ("90:10", 22), 2: ("80:20", 9), 3: ("70:30", 3), 4: ("60:40", 1), 5: ("50:50", 0)},   # 영상6: 스쿨존
    {0: ("100:0", 15), 1: ("90:10", 18), 2: ("80:20", 22), 3: ("70:30", 28), 4: ("60:40", 12), 5: ("50:50", 5)},# 영상7: 우회전 오토바이 (분쟁)
    {0: ("100:0", 82), 1: ("90:10", 12), 2: ("80:20", 4), 3: ("70:30", 1), 4: ("60:40", 1), 5: ("50:50", 0)},   # 영상8: 음주운전
    {0: ("100:0", 10), 1: ("90:10", 15), 2: ("80:20", 20), 3: ("70:30", 30), 4: ("60:40", 18), 5: ("50:50", 7)},# 영상9: 차선변경 (분쟁)
    {0: ("100:0", 88), 1: ("90:10", 9), 2: ("80:20", 2), 3: ("70:30", 1), 4: ("60:40", 0), 5: ("50:50", 0)},    # 영상10: 중앙선침범
    {0: ("100:0", 20), 1: ("90:10", 22), 2: ("80:20", 25), 3: ("70:30", 20), 4: ("60:40", 10), 5: ("50:50", 3)},# 영상11: 빗길 (분쟁)
]

# 가상 유저 ID pool (실제 없는 유저지만 vote 테이블엔 FK 체크가 SQLite에서 기본 비활성이라 삽입 가능)
# 대신 기존 5명 유저를 재사용하되, 영상별로 랜덤하게 배분
all_user_ids = [u.id for u in users]

# 각 영상에 가상 투표 수 생성 (실제 DB 유저 수가 적으므로 votes를 비율로만 저장)
# 현실적으로는 실제 유저만 투표 가능하지만 seed에서는 총 투표수 대신 비율 데이터를 직접 넣기엔 스키마 맞지 않음
# → 기존 5명이 각 영상에 1표씩 투표 (실제 과반 비율로 ratio 선택)
for video_idx, dist in enumerate(vote_distributions):
    # 가장 높은 비율의 ratio 선택
    dominant_ratio = max(dist.values(), key=lambda x: x[1])[0]
    # user별로 다양한 비율 분배
    ratio_choices = [dist[i][0] for i in range(6)]
    weights = [dist[i][1] for i in range(6)]
    for user in users:
        chosen = random.choices(ratio_choices, weights=weights, k=1)[0]
        db.add(Vote(
            video_id=videos[video_idx].id,
            user_id=user.id,
            ratio=chosen,
        ))
db.commit()

print(f"""
✅ Seed 완료!

유저: {len(users)}명
영상: {len(videos)}개
태그: {sum(len(t[1]) for t in tags_data)}개
사건상태: {len(status_data)}개
투표: {len(users) * len(videos)}개 (영상당 5표)
""")
