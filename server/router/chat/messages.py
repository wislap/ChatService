from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.future import select
from sqlalchemy import func, desc, asc
from typing import List, Optional
import uuid
import time
from datetime import datetime

from db.models import ChatMessage, User
from db.database import AsyncSessionLocal
from logger import logger

router = APIRouter()

# --- Pydantic Models ---
class MessageCreateRequest(BaseModel):
    content: str
    message_type: str = "text"
    sender_name: str = "匿名用户"
    alt_text: Optional[str] = None
    timestamp: Optional[float] = None

class MessageResponse(BaseModel):
    id: str
    sender: str
    content: str
    timestamp: float
    type: str
    alt: Optional[str] = None
    likes: int
    liked: bool = False
    editable: bool = True
    showButtons: bool = True
    customButtons: Optional[List[dict]] = None

class MessageLikeRequest(BaseModel):
    # 匿名点赞不需要用户ID，只需要请求体即可
    pass

class MessageUpdateRequest(BaseModel):
    content: str

class PaginatedMessagesResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    has_more: bool
    page: int
    page_size: int

# --- API Endpoints ---

@router.get("/messages/", response_model=PaginatedMessagesResponse)
async def get_messages(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="排序方式")
):
    """
    获取聊天消息列表（分页）
    """
    async with AsyncSessionLocal() as session:
        try:
            # 计算总数
            total_result = await session.execute(
                select(func.count(ChatMessage.id)).where(ChatMessage.is_deleted == False)
            )
            total = total_result.scalar()
            
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 构建查询
            query = select(ChatMessage).where(ChatMessage.is_deleted == False)
            
            # 排序：最新消息在前面
            if sort_order == "desc":
                query = query.order_by(desc(ChatMessage.timestamp))
            else:
                query = query.order_by(asc(ChatMessage.timestamp))
            
            # 分页
            query = query.offset(offset).limit(page_size)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            # 转换为响应格式
            message_responses = []
            for msg in messages:
                response = MessageResponse(
                    id=msg.message_id,
                    sender=msg.sender_name,
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
            
            has_more = offset + len(messages) < total
            
            return PaginatedMessagesResponse(
                messages=message_responses,
                total=total,
                has_more=has_more,
                page=page,
                page_size=page_size
            )
            
        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            raise HTTPException(status_code=500, detail="获取消息失败")

@router.post("/messages/", response_model=MessageResponse)
async def create_message(request: MessageCreateRequest):
    """
    创建新的聊天消息
    """
    async with AsyncSessionLocal() as session:
        try:
            # 生成唯一的消息ID（基于UUID和时间戳）
            message_id = f"msg_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
            
            # 如果没有提供时间戳，使用当前时间
            timestamp = request.timestamp or time.time()
            
            # 创建新消息
            new_message = ChatMessage(
                message_id=message_id,
                sender_name=request.sender_name,
                content=request.content,
                message_type=request.message_type,
                alt_text=request.alt_text,
                timestamp=timestamp
            )
            
            session.add(new_message)
            await session.commit()
            await session.refresh(new_message)
            
            # 返回响应
            return MessageResponse(
                id=new_message.message_id,
                sender=new_message.sender_name,
                content=new_message.content,
                timestamp=new_message.timestamp,
                type=new_message.message_type,
                alt=new_message.alt_text,
                likes=new_message.likes,
                editable=new_message.is_editable,
                showButtons=new_message.show_buttons,
                customButtons=new_message.custom_buttons
            )
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating message: {e}")
            raise HTTPException(status_code=500, detail="创建消息失败")

@router.post("/messages/{message_id}/like", response_model=dict)
async def like_message(message_id: str, request: MessageLikeRequest):
    """
    点赞消息（匿名无限点赞）
    """
    async with AsyncSessionLocal() as session:
        try:
            # 查找消息
            result = await session.execute(
                select(ChatMessage).where(ChatMessage.message_id == message_id)
            )
            message = result.scalars().first()
            
            if not message:
                raise HTTPException(status_code=404, detail="消息不存在")
            
            if message.is_deleted:
                raise HTTPException(status_code=404, detail="消息已删除")
            
            # 执行匿名点赞操作
            message.like()  # 匿名无限点赞，每次都增加点赞数
            await session.commit()
            
            return {
                "message_id": message_id,
                "likes": message.likes,
                "liked": True  # 匿名点赞总是返回True
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Error liking message: {e}")
            raise HTTPException(status_code=500, detail="点赞操作失败")

@router.delete("/messages/{message_id}", response_model=dict)
async def delete_message(message_id: str):
    """
    软删除消息
    """
    async with AsyncSessionLocal() as session:
        try:
            # 查找消息
            result = await session.execute(
                select(ChatMessage).where(ChatMessage.message_id == message_id)
            )
            message = result.scalars().first()
            
            if not message:
                raise HTTPException(status_code=404, detail="消息不存在")
            
            # 软删除
            message.is_deleted = True
            await session.commit()
            
            return {"message": "消息删除成功", "message_id": message_id}
            
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting message: {e}")
            raise HTTPException(status_code=500, detail="删除消息失败")

@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(message_id: str, request: MessageUpdateRequest):
    """
    更新消息内容
    """
    async with AsyncSessionLocal() as session:
        try:
            # 查找消息
            result = await session.execute(
                select(ChatMessage).where(ChatMessage.message_id == message_id)
            )
            message = result.scalars().first()
            
            if not message:
                raise HTTPException(status_code=404, detail="消息不存在")
            
            if not message.is_editable:
                raise HTTPException(status_code=403, detail="消息不可编辑")
            
            # 更新内容
            message.content = request.content
            message.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(message)
            
            # 返回更新后的消息
            return MessageResponse(
                id=message.message_id,
                sender=message.sender_name,
                content=message.content,
                timestamp=message.timestamp,
                type=message.message_type,
                alt=message.alt_text,
                likes=message.likes,
                editable=message.is_editable,
                showButtons=message.show_buttons,
                customButtons=message.custom_buttons
            )
            
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating message: {e}")
            raise HTTPException(status_code=500, detail="更新消息失败")

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str):
    """
    获取单个消息详情
    """
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(
                select(ChatMessage).where(ChatMessage.message_id == message_id)
            )
            message = result.scalars().first()
            
            if not message:
                raise HTTPException(status_code=404, detail="消息不存在")
            
            if message.is_deleted:
                raise HTTPException(status_code=404, detail="消息已删除")
            
            return MessageResponse(
                id=message.message_id,
                sender=message.sender_name,
                content=message.content,
                timestamp=message.timestamp,
                type=message.message_type,
                alt=message.alt_text,
                likes=message.likes,
                editable=message.is_editable,
                showButtons=message.show_buttons,
                customButtons=message.custom_buttons
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching message: {e}")
            raise HTTPException(status_code=500, detail="获取消息失败")
