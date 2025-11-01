#!/usr/bin/env python3
import sqlite3
import sys

def check_database():
    """检查数据库中的消息数据"""
    try:
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='chat_messages'")
        table_info = cursor.fetchone()
        print("表结构:")
        print(table_info[0] if table_info else "表不存在")
        print("-" * 50)
        
        # 检查未删除消息总数
        cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE is_deleted = 0")
        total_count = cursor.fetchone()[0]
        print(f"未删除消息总数: {total_count}")
        
        if total_count == 0:
            print("数据库中没有未删除的消息!")
            # 检查所有消息（包括删除的）
            cursor.execute("SELECT COUNT(*) FROM chat_messages")
            all_count = cursor.fetchone()[0]
            print(f"所有消息总数（包括删除的）: {all_count}")
            
            if all_count > 0:
                print("检查删除状态分布:")
                cursor.execute("SELECT is_deleted, COUNT(*) FROM chat_messages GROUP BY is_deleted")
                for row in cursor.fetchall():
                    print(f"  is_deleted={row[0]}: {row[1]} 条消息")
        else:
            print("最近3条消息:")
            cursor.execute("""
                SELECT id, message_id, sender_name, content, timestamp, message_type, is_deleted 
                FROM chat_messages 
                WHERE is_deleted = 0 
                ORDER BY timestamp DESC 
                LIMIT 3
            """)
            rows = cursor.fetchall()
            for row in rows:
                print(f"  ID: {row[0]}, Message_ID: {row[1]}, Sender: {row[2]}, Type: {row[5]}, Deleted: {row[6]}")
                print(f"  Content: {row[3][:50]}...")
                print(f"  Timestamp: {row[4]}")
                print()
        
        conn.close()
        return total_count > 0
        
    except Exception as e:
        print(f"数据库检查失败: {e}")
        return False

if __name__ == "__main__":
    check_database()
