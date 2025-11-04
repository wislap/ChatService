from fastapi import APIRouter, HTTPException, Response, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.future import select
from sqlalchemy import func, asc, desc
from typing import List, Optional
import json
from datetime import datetime, timedelta
from jose import jwt, JWTError

from db.models import ChatMessage, User
from db.database import get_async_session
from logger import logger
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# JWT配置
SECRET_KEY = "your_secret"

router = APIRouter()
from ChatMessage_pb2 import (
    ChatMessageResponse as PBChatMessageResponse,
    MessagesListResponse as PBMessagesListResponse,
)

# --- JWT验证函数 ---
async def get_current_user(request: Request):
    """验证JWT token并获取当前用户信息"""
    try:
        # 从Authorization header中获取token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail={"code": "NO_TOKEN", "message": "未提供认证token"})
        
        token = auth_header.split(" ")[1]  # 移除 "Bearer " 前缀
        
        # 验证token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "无效的认证token"})
        except JWTError:
            raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "无效的认证token"})
        
        # 从数据库获取用户信息
        async with get_async_session() as session:
            result = await session.execute(select(User).where(User.id == int(user_id)))
            user = result.scalars().first()
            if user is None:
                raise HTTPException(status_code=401, detail={"code": "USER_NOT_FOUND", "message": "用户不存在"})
            
            if user.is_banned:
                raise HTTPException(status_code=403, detail={"code": "USER_BANNED", "message": "账户已被封禁"})
            
            return user
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(status_code=500, detail={"code": "SERVER_ERROR", "message": "服务器内部错误"})

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

class CreateMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="消息内容")
    message_type: str = Field("text", description="消息类型")

class CreateMessageResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None
    db_id: Optional[int] = None
    timestamp: Optional[float] = None
    error: Optional[str] = None

# --- Helper Functions ---
async def get_messages_from_db(session, limit=None):
    """从数据库获取消息"""
    try:
        # 构建基本查询，只获取未删除的消息
        query = select(ChatMessage).where(ChatMessage.is_deleted == 0)
        
        # 添加排序（按时间戳降序）
        query = query.order_by(asc(ChatMessage.timestamp))
        # query = query.order_by(desc(ChatMessage.id)) 
        
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
            # logger.info(f"消息详情: DB_ID={msg.id}, User_ID={msg.sender_id or 0}, Username={msg.sender_name}, Message_ID={msg.message_id}, Content={msg.content[:50]}...")
        
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

async def create_message(message_data: CreateMessageRequest, user: User):
    """创建新消息"""
    async with get_async_session() as session:
        try:
            # 生成消息ID和时间戳
            message_id = f"msg_{int(datetime.now().timestamp() * 1000000)}"
            timestamp = datetime.now().timestamp()
            
            # 创建新消息
            new_message = ChatMessage(
                message_id=message_id,
                sender_id=user.id,  # 从JWT获取的用户ID
                sender_name=user.username,  # 从JWT获取的用户名
                content=message_data.content,
                message_type=message_data.message_type,
                timestamp=timestamp,
                likes=0,
                is_editable=True,
                show_buttons=True,
                custom_buttons=None,
                alt_text=None,
                is_deleted=False
            )
            
            session.add(new_message)
            await session.commit()
            await session.refresh(new_message)
            
            logger.info(f"新消息已创建: {message_id}, DB_ID={new_message.id}")
            
            return CreateMessageResponse(
                success=True,
                message_id=message_id,
                db_id=new_message.id,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            await session.rollback()
            return CreateMessageResponse(
                success=False,
                error=str(e)
            )

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

@router.post("/messages/send", response_model=CreateMessageResponse)
async def send_message(request: CreateMessageRequest, current_user: User = Depends(get_current_user)):
    """
    发送新消息（需要JWT认证）
    """
    try:
        logger.info(f"收到新消息发送请求: {current_user.username} - {request.content}")
        
        # 创建消息
        result = await create_message(request, current_user)
        
        if result.success:
            logger.info(f"消息发送成功: {result.message_id}")
            return result
        else:
            logger.error(f"消息发送失败: {result.error}")
            raise HTTPException(status_code=500, detail=f"消息发送失败: {result.error}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        raise HTTPException(status_code=500, detail="发送消息失败")

@router.post("/messages/protobuf", response_class=Response)
async def get_messages_protobuf(request: GetMessagesRequest):
    """
    以 Protobuf 二进制形式返回消息列表
    Content-Type: application/x-protobuf
    """
    async with get_async_session() as session:
        try:
            db_resp = await get_messages_from_db(session, request.limit)
            
            # 组装 Protobuf
            pb_list = PBMessagesListResponse()
            for item in db_resp.messages:
                pb_msg = PBChatMessageResponse(
                    user_id=item.user_id,
                    username=item.username,
                    message_id=item.message_id,
                    db_id=item.db_id,
                    content=item.content,
                    timestamp=item.timestamp,
                    type=item.type,
                    alt=item.alt or "",
                    likes=item.likes,
                    liked=item.liked,
                    editable=item.editable,
                    show_buttons=item.showButtons,
                    custom_buttons=(
                        json.dumps(item.customButtons, ensure_ascii=False)
                        if item.customButtons is not None else ""
                    ),
                )
                pb_list.messages.append(pb_msg)
            pb_list.total = db_resp.total
            pb_list.has_more = db_resp.has_more

            payload = pb_list.SerializeToString()
            return Response(
                content=payload,
                media_type="application/x-protobuf",
                headers={"Content-Disposition": 'attachment; filename="messages.pb"'},
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in get_messages_protobuf: {e}")
            raise HTTPException(status_code=500, detail="获取 Protobuf 消息失败")
