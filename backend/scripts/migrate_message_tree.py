"""
数据库迁移脚本：为消息表添加树形结构字段
添加 parent_id 和 sibling_index 字段，支持消息的父子关系和版本管理
"""
import sqlite3
import os
from pathlib import Path

def migrate_database(db_path: str):
    """迁移数据库，添加树形结构字段"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 添加 parent_id 字段（如果不存在）
        if 'parent_id' not in columns:
            print("添加 parent_id 字段...")
            cursor.execute("""
                ALTER TABLE messages 
                ADD COLUMN parent_id INTEGER 
                REFERENCES messages(message_id) ON DELETE CASCADE
            """)
            print("✅ parent_id 字段已添加")
        else:
            print("ℹ️  parent_id 字段已存在")
        
        # 添加 sibling_index 字段（如果不存在）
        if 'sibling_index' not in columns:
            print("添加 sibling_index 字段...")
            cursor.execute("""
                ALTER TABLE messages 
                ADD COLUMN sibling_index INTEGER DEFAULT 0
            """)
            print("✅ sibling_index 字段已添加")
        else:
            print("ℹ️  sibling_index 字段已存在")
        
        # 为现有数据建立父子关系
        # 假设现有的消息是成对出现的（user, assistant, user, assistant...）
        print("\n建立现有消息的父子关系...")
        cursor.execute("""
            SELECT message_id, session_id, role, created_at 
            FROM messages 
            ORDER BY session_id, created_at
        """)
        messages = cursor.fetchall()
        
        # 按会话分组
        sessions = {}
        for msg_id, session_id, role, created_at in messages:
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append((msg_id, role, created_at))
        
        # 为每个会话建立父子关系
        updated_count = 0
        for session_id, msgs in sessions.items():
            user_msg_id = None
            for i, (msg_id, role, created_at) in enumerate(msgs):
                if role == 'user':
                    # 用户消息：parent_id 为 NULL，sibling_index 为 0
                    cursor.execute("""
                        UPDATE messages 
                        SET parent_id = NULL, sibling_index = 0 
                        WHERE message_id = ?
                    """, (msg_id,))
                    user_msg_id = msg_id
                    updated_count += 1
                elif role == 'assistant' and user_msg_id is not None:
                    # 助手消息：parent_id 为用户消息ID，sibling_index 为 0（第一个版本）
                    cursor.execute("""
                        UPDATE messages 
                        SET parent_id = ?, sibling_index = 0 
                        WHERE message_id = ?
                    """, (user_msg_id, msg_id))
                    updated_count += 1
                    user_msg_id = None  # 重置，等待下一个用户消息
        
        print(f"✅ 已更新 {updated_count} 条消息的父子关系")
        
        conn.commit()
        print("\n✅ 数据库迁移完成！")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # 查找数据库文件
    script_dir = Path(__file__).parent.parent
    db_path = script_dir / "data" / "agentic_chat.db"
    
    if not db_path.exists():
        # 尝试其他可能的位置
        db_path = script_dir.parent / "data" / "agentic_chat.db"
    
    if not db_path.exists():
        print(f"❌ 未找到数据库文件: {db_path}")
        print("请确保数据库文件存在，或手动指定路径")
    else:
        print(f"📁 数据库路径: {db_path}")
        migrate_database(str(db_path))

