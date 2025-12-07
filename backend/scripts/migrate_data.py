"""
数据迁移脚本：从旧SQLite数据库迁移到新SQLAlchemy数据库
"""
import sqlite3
from app.db.database import get_db
from app.db.models import Session, Message, Project
from datetime import datetime

def migrate_data():
    """迁移历史数据"""
    
    # 连接旧数据库
    old_db_path = "data/agentic_chat.db"
    old_conn = sqlite3.connect(old_db_path)
    old_conn.row_factory = sqlite3.Row
    old_cursor = old_conn.cursor()
    
    print("🔄 开始数据迁移...")
    
    with get_db() as db:
        # 1. 迁移Sessions
        print("\n📦 迁移Sessions...")
        old_cursor.execute("SELECT * FROM sessions")
        sessions = old_cursor.fetchall()
        
        for s in sessions:
            # 检查是否已存在
            existing = db.query(Session).filter(Session.session_id == s['session_id']).first()
            if existing:
                print(f"  ⏭️  跳过已存在: {s['session_id']}")
                continue
            
            new_session = Session(
                session_id=s['session_id'],
                user_id=s.get('user_id', 'default_user'),
                title=s.get('title', '新对话'),
                project_id=s.get('project_id'),
                is_starred=bool(s.get('is_starred', 0)),
                tags=s.get('tags'),
                created_at=datetime.fromisoformat(s['created_at']) if s.get('created_at') else datetime.utcnow(),
                updated_at=datetime.fromisoformat(s['updated_at']) if s.get('updated_at') else datetime.utcnow()
            )
            db.add(new_session)
            print(f"  ✅ 迁移: {s['session_id']} - {s.get('title', 'Untitled')}")
        
        db.flush()
        print(f"✅ Sessions迁移完成: {len(sessions)}条")
        
        # 2. 迁移Messages
        print("\n💬 迁移Messages...")
        old_cursor.execute("SELECT * FROM messages")
        messages = old_cursor.fetchall()
        
        for m in messages:
            try:
                new_message = Message(
                    session_id=m['session_id'],
                    role=m['role'],
                    content=m['content'],
                    agent_type=m['agent_type'] if 'agent_type' in m.keys() else None,
                    model=m['model'] if 'model' in m.keys() else 'gpt-4o',
                    created_at=datetime.fromisoformat(m['created_at']) if 'created_at' in m.keys() and m['created_at'] else datetime.utcnow()
                )
                db.add(new_message)
            except Exception as e:
                print(f"  ⚠️  跳过消息: {e}")
        
        db.flush()
        print(f"✅ Messages迁移完成: {len(messages)}条")
        
        # 3. 迁移Projects（如果有）
        try:
            print("\n📁 迁移Projects...")
            old_cursor.execute("SELECT * FROM projects")
            projects = old_cursor.fetchall()
            
            for p in projects:
                existing = db.query(Project).filter(Project.project_id == p['project_id']).first()
                if existing:
                    continue
                
                new_project = Project(
                    project_id=p['project_id'],
                    name=p['name'],
                    description=p.get('description'),
                    color=p.get('color', 'blue'),
                    icon=p.get('icon', '📁'),
                    created_at=datetime.fromisoformat(p['created_at']) if p.get('created_at') else datetime.utcnow()
                )
                db.add(new_project)
            
            db.flush()
            print(f"✅ Projects迁移完成: {len(projects)}条")
        except sqlite3.OperationalError:
            print("⚠️  Projects表不存在，跳过")
    
    old_conn.close()
    print("\n🎉 数据迁移完成！")

if __name__ == "__main__":
    migrate_data()
