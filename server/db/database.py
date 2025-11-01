from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
import os

DATABASE_URL = "sqlite+aiosqlite:///./chat.db"  # 使用相对路径，指向server目录下的chat.db

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# 创建session工厂
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

@asynccontextmanager
async def get_async_session():
    """异步会话上下文管理器"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

Base = declarative_base()
