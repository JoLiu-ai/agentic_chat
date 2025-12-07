/**
 * 工具函数
 */
import type { AgentType } from '../types';

/**
 * 获取 Agent 配置
 */
export const getAgentConfig = (agentType: AgentType | string) => {
  const configs: Record<string, { icon: string; name: string; color: string }> = {
    router: { icon: '🎯', name: 'Router', color: '#8B5CF6' },
    researcher: { icon: '🔍', name: 'Researcher', color: '#3B82F6' },
    coder: { icon: '💻', name: 'Coder', color: '#10B981' },
    assistant: { icon: '💬', name: 'Assistant', color: '#F59E0B' },
    error: { icon: '❌', name: 'Error', color: '#EF4444' },
  };
  
  return configs[agentType] || configs.assistant;
};

/**
 * 获取 Agent 图标
 */
export const getAgentIcon = (agentType: AgentType | string) => {
  return getAgentConfig(agentType).icon;
};

/**
 * 复制到剪贴板
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    // Fallback
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return true;
    } catch (e) {
      document.body.removeChild(textarea);
      return false;
    }
  }
};

/**
 * 格式化时间
 */
export const formatTime = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * 格式化日期
 */
export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const dateOnly = new Date(d.getFullYear(), d.getMonth(), d.getDate());
  
  if (dateOnly.getTime() === today.getTime()) {
    return '今天';
  } else if (dateOnly.getTime() === yesterday.getTime()) {
    return '昨天';
  } else {
    return d.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
    });
  }
};

/**
 * 分组会话按时间
 */
export const groupSessionsByTime = (sessions: Session[]) => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const lastWeek = new Date(today);
  lastWeek.setDate(lastWeek.getDate() - 7);
  
  const groups = {
    starred: [] as Session[],
    today: [] as Session[],
    yesterday: [] as Session[],
    lastWeek: [] as Session[],
    earlier: [] as Session[],
  };
  
  sessions.forEach((session) => {
    const sessionDate = new Date(session.created_at);
    
    if (session.is_starred) {
      groups.starred.push(session);
    } else if (sessionDate >= today) {
      groups.today.push(session);
    } else if (sessionDate >= yesterday) {
      groups.yesterday.push(session);
    } else if (sessionDate >= lastWeek) {
      groups.lastWeek.push(session);
    } else {
      groups.earlier.push(session);
    }
  });
  
  return groups;
};

/**
 * 生成会话 ID
 */
export const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Debounce 函数
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * 调整文本域高度
 */
export const adjustTextareaHeight = (textarea: HTMLTextAreaElement) => {
  textarea.style.height = 'auto';
  textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
};

