-- ===================================
-- Agentic Chat Database Schema
-- ===================================

-- Sessions (会话表)
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_starred BOOLEAN DEFAULT FALSE,
    project_id TEXT,
    tags TEXT,  -- JSON array
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL
);

-- Messages (消息表) - 支持树形结构
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    agent_type TEXT,  -- 'researcher', 'coder', 'general_assistant'
    model TEXT DEFAULT 'gpt-4o',  -- 'gpt-4o', 'gpt-4-turbo', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- 树形结构字段
    parent_id INTEGER,  -- 父消息ID（用户消息的parent_id为NULL，助手消息的parent_id为用户消息ID）
    sibling_index INTEGER DEFAULT 0,  -- 同一父节点下的兄弟节点索引（从0开始）
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES messages(message_id) ON DELETE CASCADE
);

-- Projects (项目表)
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT 'default_user',
    name TEXT NOT NULL,
    description TEXT,
    color TEXT DEFAULT 'blue',
    icon TEXT DEFAULT '📁',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_project_id ON sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- Route History (保留原有监控表)
CREATE TABLE IF NOT EXISTS route_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    route_decision TEXT NOT NULL,
    reasoning TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_route_history_session ON route_history(session_id);
CREATE INDEX IF NOT EXISTS idx_route_history_timestamp ON route_history(timestamp DESC);
