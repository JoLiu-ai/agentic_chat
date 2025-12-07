/**
 * 全局状态管理 - Zustand
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Session, Message, Model, MessageVersion, ThemeMode } from '../types';

interface AppState {
  // 会话相关
  sessions: Session[];
  currentSessionId: string | null;
  
  // 消息相关
  messages: Message[];
  isLoading: boolean;
  thinkMode: boolean;
  
  // 模型相关
  models: Model[];
  currentModel: string;
  
  // UI 相关
  sidebarOpen: boolean;
  theme: ThemeMode;
  
  // 版本管理
  messageVersions: Record<string, MessageVersion[]>;
  pendingVersion: {
    messageId: string | null;
    versions: MessageVersion[];
  };
  // 用户消息的当前版本索引
  userMessageVersionIndex: Record<string, number>;
  
  // 上下文菜单
  contextMenuSessionId: string | null;
  
  // Actions
  setSessions: (sessions: Session[]) => void;
  setCurrentSessionId: (id: string | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  setThinkMode: (mode: boolean) => void;
  setModels: (models: Model[]) => void;
  setCurrentModel: (model: string) => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: ThemeMode) => void;
  setMessageVersions: (messageId: string, versions: MessageVersion[]) => void;
  getMessageVersions: (messageId: string) => MessageVersion[] | undefined;
  setPendingVersion: (messageId: string, versions: MessageVersion[]) => void;
  clearPendingVersion: () => void;
  setUserMessageVersionIndex: (messageId: string, index: number) => void;
  getUserMessageVersionIndex: (messageId: string) => number;
  setContextMenuSessionId: (id: string | null) => void;
  findSession: (id: string) => Session | undefined;
  clearMessages: () => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      // 初始状态
      sessions: [],
      currentSessionId: null,
      messages: [],
      isLoading: false,
      thinkMode: false,
      models: [],
      currentModel: 'gpt-4o',
      sidebarOpen: false,
      theme: 'light',
      messageVersions: {},
      pendingVersion: {
        messageId: null,
        versions: [],
      },
      userMessageVersionIndex: {},
      contextMenuSessionId: null,
      
      // Actions
      setSessions: (sessions) => set({ sessions }),
      
      setCurrentSessionId: (id) => set({ currentSessionId: id }),
      
      setMessages: (messages) => set({ messages }),
      
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, message],
      })),
      
      clearMessages: () => set({ messages: [] }),
      
      setLoading: (loading) => set({ isLoading: loading }),
      
      setThinkMode: (mode) => set({ thinkMode: mode }),
      
      setModels: (models) => set({ models }),
      
      setCurrentModel: (model) => set({ currentModel: model }),
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      setTheme: (theme) => set({ theme }),
      
      setMessageVersions: (messageId, versions) => set((state) => ({
        messageVersions: {
          ...state.messageVersions,
          [messageId]: versions,
        },
      })),
      
      getMessageVersions: (messageId) => get().messageVersions[messageId],
      
      setPendingVersion: (messageId, versions) => set({
        pendingVersion: { messageId, versions },
      }),
      
      clearPendingVersion: () => set({
        pendingVersion: { messageId: null, versions: [] },
      }),
      
      setUserMessageVersionIndex: (messageId, index) => set((state) => ({
        userMessageVersionIndex: {
          ...state.userMessageVersionIndex,
          [messageId]: index,
        },
      })),
      
      getUserMessageVersionIndex: (messageId) => {
        const state = get();
        return state.userMessageVersionIndex[messageId] ?? 0;
      },
      
      setContextMenuSessionId: (id) => set({ contextMenuSessionId: id }),
      
      findSession: (id) => get().sessions.find((s) => s.session_id === id || s.id === id),
    }),
    { name: 'AgenticChatStore' }
  )
);

