#!/usr/bin/env python3
"""
测试数据生成器 - 批量创建聊天消息（最终版）
"""
import sys
import os
import asyncio
import uuid
import time
import random
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import AsyncSessionLocal, engine
from models import Base, User, ChatMessage
from sqlalchemy import func, select

async def get_or_create_test_users(session, count=5):
    """获取或创建测试用户，避免用户名冲突"""
    # 先查询现有用户
    result = await session.execute(select(User).order_by(User.id))
    existing_users = result.scalars().all()
    
    if len(existing_users) >= count:
        print(f"✅ 已存在 {len(existing_users)} 个用户，直接使用现有用户")
        return existing_users[:count]
    
    users = list(existing_users)  # 包含现有用户
    needed = count - len(existing_users)
    
    print(f"需要创建 {needed} 个新用户")
    
    for i in range(needed):
        # 使用时间戳避免用户名冲突
        timestamp_suffix = int(time.time() * 1000000) % 10000
        user = User(
            username=f"test_user_{len(users)+1}_{timestamp_suffix}",
            email=f"test{len(users)+1}_{timestamp_suffix}@example.com",
            hashed_password="hashed_password_123",
            timestamp=datetime.utcnow()
        )
        users.append(user)
        session.add(user)
    
    await session.commit()
    print(f"✅ 总共有 {len(users)} 个测试用户")
    return users

async def generate_messages(session, users, count=20):
    """批量生成测试消息"""
    message_templates = [
        "这是第 {num} 条测试消息",
        "Hello World! 消息编号: {num}",
        "今天的天气真不错，消息 {num}",
        "学习编程真有趣，这是第 {num} 条消息",
        "大家好啊！这是第 {num} 条消息",
        "测试消息 {num} - 功能验证中",
        "这是一条关于 {topic} 的消息 {num}",
        "今天学到了新知识，分享一下 - 消息 {num}",
        "有问题需要讨论，消息 {num}",
        "分享一个有趣的内容，编号 {num}"
    ]
    
    topics = ["Python", "JavaScript", "数据库", "人工智能", "Web开发", "算法", "数据结构"]
    
    generated_messages = []
    
    for i in range(count):
        # 随机选择用户
        user = users[i % len(users)]
        
        # 随机选择模板和主题
        template = random.choice(message_templates)
        topic = random.choice(topics)
        
        # 生成消息ID
        message_id = f"msg_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
        
        # 生成消息内容
        content = template.format(num=i+1, topic=topic)
        
        # 生成随机时间戳（最近7天内）
        now = time.time()
        random_time = now - random.randint(0, 7*24*60*60)  # 7天内的随机时间
        
        # 创建消息
        message = ChatMessage(
            message_id=message_id,
            sender_id=user.id if user.id else None,
            sender_name=user.username if user.username else "匿名用户",
            content=content,
            message_type="text",
            timestamp=random_time,
            likes=0,  # 初始点赞数为0
            is_editable=True,
            show_buttons=True
        )
        
        session.add(message)
        generated_messages.append(message)
        
        # 每10条消息提交一次，避免一次性提交太多
        if (i + 1) % 10 == 0:
            await session.commit()
            print(f"已提交 {i + 1} 条消息...")
    
    # 提交剩余消息
    await session.commit()
    print(f"✅ 成功生成了 {len(generated_messages)} 条测试消息")
    
    return generated_messages

async def add_random_likes(session, messages, like_probability=0.3):
    """为消息随机添加点赞"""
    liked_count = 0
    for message in messages:
        if random.random() < like_probability:
            # 随机增加1-10个点赞
            additional_likes = random.randint(1, 10)
            message.likes += additional_likes
            liked_count += additional_likes
    
    await session.commit()
    print(f"✅ 为消息添加了总共 {liked_count} 个随机点赞")

async def main():
    """主函数"""
    print("🚀 开始生成测试数据...")
    
    # 可配置参数
    NUM_USERS = 5      # 创建的用户数量
    NUM_MESSAGES = 5  # 生成的消息数量
    LIKE_PROBABILITY = 0.4  # 消息被点赞的概率
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. 获取或创建测试用户
            print(f"\n📝 步骤1: 获取或创建 {NUM_USERS} 个测试用户")
            users = await get_or_create_test_users(session, NUM_USERS)
            
            # 2. 生成测试消息
            print(f"\n💬 步骤2: 生成 {NUM_MESSAGES} 条测试消息")
            messages = await generate_messages(session, users, NUM_MESSAGES)
            
            # 3. 随机添加点赞
            print(f"\n👍 步骤3: 随机添加点赞")
            await add_random_likes(session, messages, LIKE_PROBABILITY)
            
            # 4. 显示统计信息
            print(f"\n📊 数据统计:")
            print(f"   - 用户数量: {len(users)}")
            print(f"   - 消息数量: {len(messages)}")
            
            # 查询点赞统计
            result = await session.execute(select(func.sum(ChatMessage.likes)))
            total_likes = result.scalar() or 0
            print(f"   - 总点赞数: {total_likes}")
            
            # 查询最受欢迎的消息
            result = await session.execute(
                select(ChatMessage).order_by(ChatMessage.likes.desc()).limit(3)
            )
            top_messages = result.scalars().all()
            
            print(f"\n🏆 最受欢迎的消息:")
            for i, msg in enumerate(top_messages, 1):
                print(f"   {i}. 点赞数: {msg.likes} | 内容: {msg.content[:50]}...")
            
            print(f"\n✨ 测试数据生成完成！")
            print(f"服务器地址: http://127.0.0.1:25578")
            print(f"可以访问 /docs 查看API文档测试点赞功能")
            
        except Exception as e:
            print(f"❌ 生成测试数据时出错: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())
