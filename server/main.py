import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from router.users.login import router as user_login_router
from router.chat.messages import router as chat_router
from db.database import engine
from db.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时创建表（等同于 CREATE TABLE IF NOT EXISTS）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 在这里可以放置关闭逻辑（例如关闭连接池）
    
app = FastAPI(lifespan=lifespan)

# 包含用户认证路由
app.include_router(user_login_router, prefix="/api")

# 包含聊天消息路由
app.include_router(chat_router, prefix="/api")

origins = ["http://localhost:5173",]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=25578, reload=True)
