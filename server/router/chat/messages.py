from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.future import select
from sqlalchemy import func, desc
from typing import List, Optional

from db.models import ChatMessage
from db.database import get_async_session
from logger import logger

router = APIRouter()

# --- Pydantic Models ---
class MessageResponse(BaseModel):
    # 用户信息
    user_id: int
    username: str
    # 消息信息
    message_id: str
    db_id: int
    content: str
    timestamp: float
    type: str
    alt: Optional[str] = None
    likes: int
    liked: bool = False
    editable: bool = True
    showButtons: bool = True
    customButtons: Optional[List[dict]] = None

class GetMessagesRequest(BaseModel):
    # 分页参数
    limit: Optional[int] = Field(None, ge=1, le=1000, description="返回消息数量限制")

class MessagesListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    has_more: bool

# --- Helper Functions ---
async def get_messages_from_db(session, limit=None):
    """从数据库获取全部消息"""
    try:
        # 构建基本查询，只获取未删除的消息
        query = select(ChatMessage).where(ChatMessage.is_deleted == 0)
        
        # 添加排序（按时间戳降序）
        query = query.order_by(desc(ChatMessage.timestamp))
        
        # 添加限制
        if limit:
            query = query.limit(limit)
        
        logger.info(f"执行数据库查询，limit={limit}")
        
        result = await session.execute(query)
        messages = result.scalars().all()
        
        logger.info(f"从数据库读取到 {len(messages)} 条消息")
        
        # 转换为响应格式
        message_responses = []
        for msg in messages:
            response = MessageResponse(
                user_id=msg.sender_id or 0,  # 如果 sender_id 为 None，使用 0
                username=msg.sender_name,
                message_id=msg.message_id,
                db_id=msg.id,
                content=msg.content,
                timestamp=msg.timestamp,
                type=msg.message_type,
                alt=msg.alt_text,
                likes=msg.likes,
                editable=msg.is_editable,
                showButtons=msg.show_buttons,
                customButtons=msg.custom_buttons
            )
            message_responses.append(response)
            
            # 记录每条消息的详细信息
            logger.info(f"消息详情: DB_ID={msg.id}, User_ID={msg.sender_id or 0}, Username={msg.sender_name}, Message_ID={msg.message_id}, Content={msg.content[:50]}...")
        
        # 计算总数
        total_result = await session.execute(
            select(func.count(ChatMessage.id)).where(ChatMessage.is_deleted == 0)
        )
        total = total_result.scalar()
        
        logger.info(f"数据库中未删除消息总数: {total}")
        
        has_more = limit is not None and len(messages) < total
        
        logger.info(f"返回结果: total={total}, has_more={has_more}")
        
        return MessagesListResponse(
            messages=message_responses,
            total=total,
            has_more=has_more
        )
        
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail="获取消息失败")

# --- API Endpoints ---

@router.post("/messages/", response_model=MessagesListResponse)
async def get_messages(request: GetMessagesRequest):
    
    """
    获取全部消息列表
    返回所有未删除的消息，支持限制返回数量
    """
    async with get_async_session() as session:
        try:
            logger.info("=== 开始获取消息请求 ===")
            # 获取消息
            response = await get_messages_from_db(
                session, 
                request.limit
            )
            logger.info(f"=== 请求完成，返回 {len(response.messages)} 条消息 ===")
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_messages: {e}")
            raise HTTPException(status_code=500, detail="获取消息失败")
