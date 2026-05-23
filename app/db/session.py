from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from decouple import config

DATABASE_URL = config("DATABASE_URL", default="sqlite+aiosqlite:///./app/db/mib.db")

# Railway는 postgres:// 또는 postgresql://로 제공하므로 드라이버별로 변환
if DATABASE_URL.startswith("postgres://"):
    async_database_url = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    sync_database_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    async_database_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    sync_database_url = DATABASE_URL
else:
    async_database_url = DATABASE_URL  # sqlite+aiosqlite
    sync_database_url = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

async_engine = create_async_engine(async_database_url, echo=True)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

sync_engine = create_engine(sync_database_url, echo=True)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
