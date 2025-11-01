#!/usr/bin/env python3
"""
测试API消息获取功能
"""
import requests
import json
import sys

def test_get_messages():
    """测试获取消息的API"""
    try:
        # 测试健康检查
        print("测试健康检查...")
        health_response = requests.get("http://127.0.0.1:25578/health", timeout=5)
        print(f"健康检查状态码: {health_response.status_code}")
        print(f"健康检查响应: {health_response.json()}")
        
        # 测试获取消息
        print("\n测试获取消息...")
        messages_response = requests.post(
            "http://127.0.0.1:25578/api/messages/",
            json={"limit": 10},
            timeout=5
        )
        print(f"获取消息状态码: {messages_response.status_code}")
        
        if messages_response.status_code == 200:
            data = messages_response.json()
            print(f"消息总数: {data.get('total', 0)}")
            print(f"返回消息数: {len(data.get('messages', []))}")
            print(f"是否有更多: {data.get('has_more', False)}")
            
            if data.get('messages'):
                print("最新消息:")
                for msg in data['messages'][:3]:  # 显示前3条
                    print(f"  发送者: {msg.get('username')}")
                    print(f"  内容: {msg.get('content', '')[:50]}...")
                    print(f"  消息ID: {msg.get('message_id')}")
                    print()
        else:
            print(f"错误响应: {messages_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保服务器正在运行在 http://127.0.0.1:25578")
        return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_get_messages()
