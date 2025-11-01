from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey, Text, Float
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import JSON
from datetime import datetime
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_banned = Column(Boolean, default=False)
    
    # 与聊天消息的关联
    sent_messages = relationship("ChatMessage", foreign_keys="ChatMessage.sender_id", back_populates="sender")
    
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 前端消息标识符
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # 发送者信息
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 系统消息可能没有发送者
    sender_name = Column(String(100), nullable=False, default="匿名用户")
    
    # 消息内容
    content = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False, default="text")  # markdown, text, image, system等
    
    # 图片描述（可选）
    alt_text = Column(Text, nullable=True)
    
    # 时间戳（前端传入的时间戳，用于保持同步）
    timestamp = Column(Float, nullable=False)
    
    # 点赞功能（匿名无限点赞）
    likes = Column(Integer, default=0)
    
    # 前端扩展功能
    is_editable = Column(Boolean, default=True)
    show_buttons = Column(Boolean, default=True)
    custom_buttons = Column(JSON, nullable=True)  # 自定义按钮配置
    
    # 系统字段
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # 关联关系
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender={self.sender_name}, type={self.message_type}, likes={self.likes})>"
    
    def like(self) -> None:
        """点赞（匿名无限点赞）"""
        self.likes += 1
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于API响应"""
        return {
            "id": self.message_id,
            "sender": self.sender_name,
            "content": self.content,
            "timestamp": self.timestamp,
            "type": self.message_type,
            "alt": self.alt_text,
            "likes": self.likes,
            "liked": False,  # 匿名点赞不需要显示用户点赞状态
            "editable": self.is_editable,
            "showButtons": self.show_buttons,
            "customButtons": self.custom_buttons
        }
