/**
 * API 端点定义 - 完整迁移
 */
import apiClient from './client';
import type { Session, Message, ChatRequest, ChatResponse, Model, Project } from '../types';

// ===== 会话管理 API =====

export const sessionAPI = {
  /**
   * 获取所有会话
   */
  list: (): Promise<{ sessions: Session[] }> => 
    apiClient.get('/sessions'),
  
  /**
   * 获取收藏会话
   */
  starred: (): Promise<{ sessions: Session[] }> =>
    apiClient.get('/sessions/starred'),
  
  /**
   * 创建新会话
   */
  create: (title?: string, projectId?: string): Promise<Session> =>
    apiClient.post('/sessions', {
      user_id: 'default_user',
      title: title || '新对话',
      project_id: projectId,
    }),
  
  /**
   * 获取单个会话
   */
  get: (sessionId: string): Promise<Session> =>
    apiClient.get(`/sessions/${sessionId}`),
  
  /**
   * 获取会话消息
   */
  getMessages: (sessionId: string): Promise<{ messages: Message[] }> =>
    apiClient.get(`/sessions/${sessionId}/messages`),
  
  /**
   * 更新会话
   */
  update: (sessionId: string, updates: Partial<Session>): Promise<Session> =>
    apiClient.put(`/sessions/${sessionId}`, updates),
  
  /**
   * 删除会话
   */
  delete: (sessionId: string): Promise<void> =>
    apiClient.delete(`/sessions/${sessionId}`),
  
  /**
   * 收藏/取消收藏
   */
  toggleStar: (sessionId: string, isStarred: boolean): Promise<Session> =>
    apiClient.put(`/sessions/${sessionId}`, { is_starred: isStarred }),
};

// ===== 消息管理 API =====

export const messageAPI = {
  /**
   * 发送消息
   */
  send: (sessionId: string, message: string, model?: string): Promise<ChatResponse> =>
    apiClient.post('/chat', {
      message,
      session_id: sessionId,
      user_id: 'default_user',
      model: model || 'gpt-4o',
    }),
  
  /**
   * 删除消息
   */
  delete: (messageId: string): Promise<void> =>
    apiClient.delete(`/messages/${messageId}`),
  
  /**
   * 删除消息及之后的所有消息
   */
  deleteAfter: (messageId: string): Promise<void> =>
    apiClient.delete(`/messages/${messageId}/after`),
  
  /**
   * 更新消息
   */
  update: (messageId: string, content: string): Promise<Message> =>
    apiClient.put(`/messages/${messageId}`, { content }),
};

// ===== 配置 API =====

export const configAPI = {
  /**
   * 获取可用模型列表
   */
  getModels: async (): Promise<Model[]> => {
    const response = await apiClient.get<{ models: Model[]; default: string }>('/config/models');
    return response.models || [];
  },
};

// ===== 项目管理 API =====

export const projectAPI = {
  /**
   * 获取所有项目
   */
  list: (): Promise<{ projects: Project[] }> =>
    apiClient.get('/projects'),
  
  /**
   * 创建项目
   */
  create: (name: string, description?: string, color?: string, icon?: string): Promise<Project> =>
    apiClient.post('/projects', {
      name,
      description,
      color: color || 'blue',
      icon: icon || '📁',
      user_id: 'default_user',
    }),
  
  /**
   * 删除项目
   */
  delete: (projectId: string): Promise<void> =>
    apiClient.delete(`/projects/${projectId}`),
};

// ===== 健康检查 API =====

export const healthAPI = {
  /**
   * 健康检查
   */
  check: (): Promise<{ status: string; version: string; environment: string }> =>
    axios.get(`${API_BASE_URL}/health`).then(res => res.data),
  
  /**
   * Ping
   */
  ping: (): Promise<{ ping: string }> =>
    axios.get(`${API_BASE_URL}/ping`).then(res => res.data),
  
  /**
   * 应用信息
   */
  info: (): Promise<any> =>
    axios.get(`${API_BASE_URL}/info`).then(res => res.data),
};

// ===== 导出所有 API =====

// ===== Router监控 API =====

export const routerAPI = {
  /**
   * 获取路由统计信息
   */
  getStats: (): Promise<{
    total_routes: number;
    researcher_count: number;
    coder_count: number;
    general_count: number;
    researcher_percentage: number;
    coder_percentage: number;
    general_percentage: number;
  }> => apiClient.get('/router/routes/stats'),

  /**
   * 获取路由历史记录
   */
  getHistory: (limit: number = 50): Promise<Array<{
    id: number;
    session_id: string;
    user_message: string;
    routed_to: string;
    reasoning: string;
    timestamp: string;
  }>> => apiClient.get('/router/routes/history', { params: { limit } }),

  /**
   * 获取特定会话的路由历史
   */
  getSessionRoutes: (sessionId: string): Promise<Array<{
    id: number;
    session_id: string;
    user_message: string;
    routed_to: string;
    reasoning: string;
    timestamp: string;
  }>> => apiClient.get(`/router/routes/session/${sessionId}`),
};

export const api = {
  session: sessionAPI,
  message: messageAPI,
  config: configAPI,
  project: projectAPI,
  health: healthAPI,
  router: routerAPI,
};

export default api;
