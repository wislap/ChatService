from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./chat.db"  # 使用SQLite数据库

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True,future=True)

# 创建session工厂
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()
