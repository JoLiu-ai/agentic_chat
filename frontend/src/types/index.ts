/**
 * 类型定义
 */

export interface Session {
  session_id: string;
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  is_starred?: boolean;
  project_id?: string;
  user_id: string;
}

export interface Message {
  id: string;
  message_id?: number; // 后端返回的message_id
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  updated_at?: string;
  agent_type?: string;
  metadata?: Record<string, any>;
  citations?: Citation[];
  sources?: Citation[];
  // 树形结构字段
  parent_id?: number | null; // 父消息ID（用户消息为null，助手消息为用户消息ID）
  sibling_index?: number; // 同一父节点下的兄弟节点索引（从0开始）
}

export interface Citation {
  url?: string;
  title?: string;
  domain?: string;
}

export interface ChatRequest {
  message: string;
  session_id: string;
  user_id: string;
  model?: string;
  stream?: boolean;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  agent_type?: string;
  citations?: Citation[];
  sources?: Citation[];
  message: Message;
}

export interface Model {
  value: string;
  label: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  user_id: string;
  created_at: string;
}

export interface MessageVersion {
  content: string;
  agent: string;
  timestamp: string;
}

export type ThemeMode = 'light' | 'dark';
export type AgentType = 'router' | 'researcher' | 'coder' | 'assistant' | 'error';

