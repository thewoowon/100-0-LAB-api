from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from dotenv import load_dotenv
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("uploads/thumbnails", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    from app.db.session import SyncSessionLocal
    import app.services.embedding_service as embedding_service
    db = SyncSessionLocal()
    try:
        embedding_service.load_cache(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
