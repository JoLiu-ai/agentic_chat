/**
 * RouterMonitor 组件 - Router监控仪表盘
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/endpoints';
import { logger } from '../utils/logger';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useAppStore } from '../store';
import './RouterMonitor.css';

interface RouteHistoryItem {
  id: number;
  session_id: string;
  user_message: string;
  routed_to: string;
  reasoning: string;
  timestamp: string;
}

interface RouteStats {
  total_routes: number;
  researcher_count: number;
  coder_count: number;
  general_count: number;
  researcher_percentage: number;
  coder_percentage: number;
  general_percentage: number;
}

export const RouterMonitor: React.FC = () => {
  const { sidebarOpen } = useAppStore();
  const [stats, setStats] = useState<RouteStats | null>(null);
  const [history, setHistory] = useState<RouteHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statsData, historyData] = await Promise.all([
        api.router.getStats(),
        api.router.getHistory(50),
      ]);
      
      setStats(statsData);
      setHistory(historyData);
      logger.info('Router监控数据加载成功');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '加载数据失败';
      setError(errorMessage);
      logger.error('Router监控数据加载失败', err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('zh-CN');
    } catch {
      return timestamp;
    }
  };

  const getAgentLabel = (routedTo: string) => {
    const labels: Record<string, string> = {
      researcher: 'Researcher',
      coder: 'Coder',
      general_assistant: 'General',
    };
    return labels[routedTo] || routedTo;
  };

  const getAgentColor = (routedTo: string) => {
    const colors: Record<string, string> = {
      researcher: '#3b82f6',
      coder: '#10b981',
      general_assistant: '#8b5cf6',
    };
    return colors[routedTo] || '#6b7280';
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="router-monitor-container">
          <div className="router-monitor-loading">加载中...</div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="router-monitor-container">
          <div className="router-monitor-error">
            <p>错误: {error}</p>
            <button onClick={loadData}>重试</button>
          </div>
        </div>
      );
    }

    return (
      <>
        <div className="router-monitor-container">
          <div className="router-monitor-header">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
              <div>
                <h1>🔀 Router监控仪表盘</h1>
                <p>实时查看Agent路由决策和统计信息</p>
              </div>
              <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
                <Link to="/" style={{ textDecoration: 'none' }}>
                  <button className="refresh-btn">
                    ← 返回聊天
                  </button>
                </Link>
                <button className="refresh-btn" onClick={loadData}>
                  🔄 刷新数据
                </button>
              </div>
            </div>
          </div>

          {stats && (
            <div className="router-monitor-stats">
              <h2>📊 路由统计</h2>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-label">总路由数</div>
                  <div className="stat-value">{stats.total_routes}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Researcher</div>
                  <div className="stat-value">
                    {stats.researcher_count} ({stats.researcher_percentage}%)
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Coder</div>
                  <div className="stat-value">
                    {stats.coder_count} ({stats.coder_percentage}%)
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">General</div>
                  <div className="stat-value">
                    {stats.general_count} ({stats.general_percentage}%)
                  </div>
                </div>
              </div>

              {stats.total_routes > 0 && (
                <div className="stats-chart">
                  <div className="chart-bar">
                    <div
                      className="chart-segment researcher"
                      style={{
                        width: `${stats.researcher_percentage}%`,
                        backgroundColor: getAgentColor('researcher'),
                      }}
                      title={`Researcher: ${stats.researcher_percentage}%`}
                    />
                    <div
                      className="chart-segment coder"
                      style={{
                        width: `${stats.coder_percentage}%`,
                        backgroundColor: getAgentColor('coder'),
                      }}
                      title={`Coder: ${stats.coder_percentage}%`}
                    />
                    <div
                      className="chart-segment general"
                      style={{
                        width: `${stats.general_percentage}%`,
                        backgroundColor: getAgentColor('general_assistant'),
                      }}
                      title={`General: ${stats.general_percentage}%`}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="router-monitor-history">
            <h2>📜 路由历史</h2>
            {history.length === 0 ? (
              <div className="empty-state">暂无路由历史记录</div>
            ) : (
              <div className="history-list">
                {history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-header">
                      <span
                        className="agent-badge"
                        style={{ backgroundColor: getAgentColor(item.routed_to) }}
                      >
                        {getAgentLabel(item.routed_to)}
                      </span>
                      <span className="history-timestamp">
                        {formatTimestamp(item.timestamp)}
                      </span>
                    </div>
                    <div className="history-message">{item.user_message}</div>
                    {item.reasoning && (
                      <div className="history-reasoning">
                        <strong>推理:</strong> {item.reasoning}
                      </div>
                    )}
                    <div className="history-session">
                      Session: {item.session_id}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </>
    );
  };

  return (
    <div 
      className={`app-container ${sidebarOpen ? 'sidebar-open' : ''}`}
      data-theme="light"
    >
      <Header />
      
      <div className="container">
        <Sidebar
          onSessionClick={() => {}}
          onNewChat={() => {}}
          onSessionAction={() => {}}
        />
        
        <main className="main-content">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

