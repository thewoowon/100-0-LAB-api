from fastapi import APIRouter
from app.api.v1.endpoints import user, auth, video, vote, tag, case_status, comment, submission

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(video.router, prefix="/videos", tags=["videos"])
api_router.include_router(vote.router, prefix="/videos", tags=["votes"])
api_router.include_router(tag.router, prefix="/videos", tags=["tags"])
api_router.include_router(case_status.router, prefix="/videos", tags=["case-status"])
api_router.include_router(comment.router, prefix="/videos", tags=["comments"])
api_router.include_router(submission.router, prefix="/submissions", tags=["submissions"])
