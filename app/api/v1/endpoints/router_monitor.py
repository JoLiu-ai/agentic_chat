"""
Router监控API - 路由决策历史和统计
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import sqlite3

router = APIRouter()

DB_PATH = "data/sessions.db"

# 初始化路由历史表
def init_router_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS route_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  user_message TEXT,
                  routed_to TEXT,
                  reasoning TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

init_router_db()

class RouteHistoryItem(BaseModel):
    id: int
    session_id: str
    user_message: str
    routed_to: str
    reasoning: str
    timestamp: str

class RouteStats(BaseModel):
    total_routes: int
    researcher_count: int
    coder_count: int
    general_count: int
    researcher_percentage: float
    coder_percentage: float
    general_percentage: float

@router.get("/routes/history", response_model=List[RouteHistoryItem])
async def get_route_history(limit: int = 50):
    """获取路由历史记录"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT id, session_id, user_message, routed_to, reasoning, timestamp
            FROM route_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        return [
            RouteHistoryItem(
                id=row[0],
                session_id=row[1],
                user_message=row[2],
                routed_to=row[3],
                reasoning=row[4],
                timestamp=row[5]
            )
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routes/stats", response_model=RouteStats)
async def get_route_stats():
    """获取路由统计信息"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 总路由数
        c.execute("SELECT COUNT(*) FROM route_history")
        total = c.fetchone()[0]
        
        # 各Agent统计
        c.execute("SELECT routed_to, COUNT(*) FROM route_history GROUP BY routed_to")
        counts = dict(c.fetchall())
        conn.close()
        
        researcher_count = counts.get("researcher", 0)
        coder_count = counts.get("coder", 0)
        general_count = counts.get("general_assistant", 0)
        
        return RouteStats(
            total_routes=total,
            researcher_count=researcher_count,
            coder_count=coder_count,
            general_count=general_count,
            researcher_percentage=round(researcher_count / total * 100, 2) if total > 0 else 0,
            coder_percentage=round(coder_count / total * 100, 2) if total > 0 else 0,
            general_percentage=round(general_count / total * 100, 2) if total > 0 else 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routes/session/{session_id}", response_model=List[RouteHistoryItem])
async def get_session_routes(session_id: str):
    """获取特定会话的路由历史"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT id, session_id, user_message, user_message, routed_to, reasoning, timestamp
            FROM route_history
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))
        
        rows = c.fetchall()
        conn.close()
        
        return [
            RouteHistoryItem(
                id=row[0],
                session_id=row[1],
                user_message=row[2],
                routed_to=row[3],
                reasoning=row[4],
                timestamp=row[5]
            )
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def log_route_decision(session_id: str, user_message: str, routed_to: str, reasoning: str):
    """记录路由决策（供Router调用）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO route_history (session_id, user_message, routed_to, reasoning, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, user_message, routed_to, reasoning, datetime.now().isoformat()))
    conn.commit()
    conn.close()
