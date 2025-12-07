/**
 * Sidebar 组件 - 会话列表
 */
import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store';
import { api } from '../api/endpoints';
import { groupSessionsByTime } from '../utils/helpers';
import type { Session } from '../types';

interface SessionItemProps {
  session: Session;
  isActive: boolean;
  icon: string;
  onClick: () => void;
  onMore: (e: React.MouseEvent) => void;
}

const SessionItem: React.FC<SessionItemProps> = ({ session, isActive, icon, onClick, onMore }) => {
  return (
    <div
      className={`session-item-new ${isActive ? 'active' : ''}`}
      data-session-id={session.session_id || session.id}
      onClick={onClick}
    >
      <span className="session-icon">{icon}</span>
      <span className="session-title-new">{session.title || '未命名对话'}</span>
      <button 
        className="session-more-btn" 
        title="更多操作"
        onClick={onMore}
      >
        ⋯
      </button>
    </div>
  );
};

export const Sidebar: React.FC<{
  onSessionClick: (sessionId: string) => void;
  onNewChat: () => void;
  onSessionAction: (sessionId: string, action: string) => void;
}> = ({ onSessionClick, onNewChat, onSessionAction }) => {
  const { sessions, currentSessionId, sidebarOpen, setSessions } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [contextMenuSession, setContextMenuSession] = useState<string | null>(null);
  const [contextMenuPos, setContextMenuPos] = useState({ x: 0, y: 0 });
  
  useEffect(() => {
    loadSessions();
  }, []);
  
  const loadSessions = async () => {
    try {
      const data = await api.session.list();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
      setSessions([]);
    }
  };
  
  const handleMoreClick = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    setContextMenuSession(sessionId);
    setContextMenuPos({ x: e.clientX, y: e.clientY });
  };
  
  const handleContextAction = (action: string) => {
    if (contextMenuSession) {
      onSessionAction(contextMenuSession, action);
      setContextMenuSession(null);
    }
  };
  
  // 分组会话
  const groups = groupSessionsByTime(sessions);
  
  // 过滤会话
  const filterSessions = (sessionList: Session[]) => {
    if (!searchQuery.trim()) return sessionList;
    const query = searchQuery.toLowerCase();
    return sessionList.filter((s) => 
      s.title?.toLowerCase().includes(query)
    );
  };
  
  const renderGroup = (title: string, sessionList: Session[], icon: string) => {
    const filtered = filterSessions(sessionList);
    if (filtered.length === 0) return null;
    
    return (
      <div className="time-group">
        <div className="time-group-header">{title}</div>
        <div className="session-items">
          {filtered.map((session) => (
            <SessionItem
              key={session.session_id || session.id}
              session={session}
              isActive={session.session_id === currentSessionId || session.id === currentSessionId}
              icon={icon}
              onClick={() => onSessionClick(session.session_id || session.id)}
              onMore={(e) => handleMoreClick(e, session.session_id || session.id)}
            />
          ))}
        </div>
      </div>
    );
  };
  
  const hasAnySessions = sessions.length > 0;
  
  return (
    <>
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`} id="sidebar">
        {/* Header */}
        <div className="sidebar-header-compact">
          <button 
            className="new-chat-button-compact" 
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onNewChat();
            }}
            type="button"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 5v14M5 12h14" strokeWidth="2" strokeLinecap="round" />
            </svg>
            新建
          </button>
          <div className="search-input-wrapper">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="search-icon">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <input
              type="text"
              placeholder="搜索..."
              className="search-input-compact"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        {/* Session List */}
        <div className="sidebar-content-new">
          {hasAnySessions ? (
            <>
              {groups.starred.length > 0 && renderGroup('⭐ 收藏', groups.starred, '⭐')}
              {groups.today.length > 0 && renderGroup('今天', groups.today, '💬')}
              {groups.yesterday.length > 0 && renderGroup('昨天', groups.yesterday, '💬')}
              {groups.lastWeek.length > 0 && renderGroup('最近7天', groups.lastWeek, '💬')}
              {groups.earlier.length > 0 && renderGroup('更早', groups.earlier, '💬')}
            </>
          ) : (
            <div className="sidebar-empty">
              <p>暂无对话</p>
              <p className="sidebar-empty-hint">点击"新建"开始对话</p>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="sidebar-footer-new">
          <a href="/router-monitor" className="footer-link" target="_blank" title="Router监控">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M18 20V10M12 20V4M6 20v-6" />
            </svg>
          </a>
          <button className="footer-link" title="设置">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v6m0 6v10" />
            </svg>
          </button>
        </div>
      </aside>
      
      {/* Context Menu */}
      {contextMenuSession && (
        <>
          <div 
            className="context-menu-overlay"
            onClick={() => setContextMenuSession(null)}
          />
          <div
            className="context-menu visible"
            style={{
              left: `${contextMenuPos.x}px`,
              top: `${contextMenuPos.y}px`,
            }}
          >
            <div className="context-menu-item" onClick={() => handleContextAction('star')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
              <span>
                {sessions.find(s => (s.session_id || s.id) === contextMenuSession)?.is_starred ? 'Unstar' : 'Star'}
              </span>
            </div>
            <div className="context-menu-item" onClick={() => handleContextAction('rename')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
              <span>Rename</span>
            </div>
            <div className="context-menu-divider" />
            <div className="context-menu-item context-menu-item-danger" onClick={() => handleContextAction('delete')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
              </svg>
              <span>Delete</span>
            </div>
          </div>
        </>
      )}
    </>
  );
};

