import asyncio
from database import engine
from models import Base

async def init_db():
    async with engine.begin() as conn:
        # 删除已存在表再重建（如果你希望干净的数据库）
        # await conn.run_sync(Base.metadata.drop_all)

        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
