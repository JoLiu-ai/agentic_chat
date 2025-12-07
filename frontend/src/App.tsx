/**
 * App 组件 - 主应用
 * 完整迁移所有原功能
 */
import React, { useEffect, useState, useRef, useMemo } from 'react';
import { useAppStore } from './store';
import { api } from './api/endpoints';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { WelcomeScreen } from './components/WelcomeScreen';
import { Message } from './components/Message';
import { ChatInput } from './components/ChatInput';
import { logger } from './utils/logger';
import type { Model } from './types';
import './styles/main.css';

const App: React.FC = () => {
  const {
    sessions,
    setSessions,
    currentSessionId,
    setCurrentSessionId,
    messages,
    setMessages,
    addMessage,
    clearMessages,
    setLoading,
    currentModel,
    sidebarOpen,
    theme,
  } = useAppStore();
  
  const [models, setModels] = useState<Model[]>([]);
  const [showWelcome, setShowWelcome] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 初始化（只执行一次）
  useEffect(() => {
    initApp();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // 空依赖数组，确保只执行一次
  
  // 自动滚动到底部
  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages.length]); // 只依赖messages的长度，避免频繁滚动
  
  // 监听会话变化
  useEffect(() => {
    if (currentSessionId && messages.length > 0) {
      setShowWelcome(false);
    }
  }, [currentSessionId, messages.length]); // 只依赖长度，避免不必要的更新
  
  const initApp = async () => {
    logger.info('应用初始化开始');
    try {
      // 加载会话列表
      await loadSessions();
      
      // 加载模型列表
      const modelData = await api.config.getModels();
      setModels(modelData || []);
      logger.info('应用初始化成功', { modelCount: modelData?.length || 0 });
    } catch (error) {
      logger.error('应用初始化失败', error as Error);
    }
  };
  
  const loadSessions = async () => {
    try {
      logger.debug('加载会话列表');
      const data = await api.session.list();
      setSessions(data.sessions || []);
      logger.info('会话列表加载成功', { count: data.sessions?.length || 0 });
    } catch (error) {
      logger.error('加载会话列表失败', error as Error);
      setSessions([]);
    }
  };
  
  const handleNewChat = () => {
    logger.info('新建对话');
    setCurrentSessionId(null);
    clearMessages();
    setShowWelcome(true);
    // 确保输入框获得焦点
    setTimeout(() => {
      const input = document.querySelector('.message-input') as HTMLTextAreaElement;
      if (input) {
        input.focus();
      }
    }, 100);
  };
  
  const handleSessionClick = async (sessionId: string) => {
    try {
      setCurrentSessionId(sessionId);
      setShowWelcome(false);
      clearMessages();
      
      // 加载消息
      const data = await api.session.getMessages(sessionId);
      setMessages(data.messages || []);
      
      // 刷新会话列表
      await loadSessions();
    } catch (error) {
      console.error('加载会话失败:', error);
      alert('加载对话失败，请重试');
    }
  };
  
  const handleSessionAction = async (sessionId: string, action: string) => {
    const session = sessions.find(s => (s.session_id || s.id) === sessionId);
    if (!session) return;
    
    switch (action) {
      case 'star':
        try {
          await api.session.toggleStar(sessionId, !session.is_starred);
          await loadSessions();
        } catch (error) {
          console.error('收藏失败:', error);
        }
        break;
        
      case 'rename':
        const newTitle = prompt('请输入新标题:', session.title);
        if (newTitle && newTitle.trim()) {
          try {
            await api.session.update(sessionId, { title: newTitle.trim() });
            await loadSessions();
          } catch (error) {
            console.error('重命名失败:', error);
            alert('重命名失败');
          }
        }
        break;
        
      case 'delete':
        if (confirm('确定要删除这个对话吗？')) {
          try {
            await api.session.delete(sessionId);
            if (sessionId === currentSessionId) {
              handleNewChat();
            }
            await loadSessions();
          } catch (error) {
            console.error('删除失败:', error);
          }
        }
        break;
    }
  };
  
  const handleSendMessage = async (messageText: string, model: string) => {
    const startTime = performance.now();
    logger.info('发送消息', { messageLength: messageText.length, model });
    
    try {
      setLoading(true);
      
      // 如果没有会话，创建新会话
      let sessionId = currentSessionId;
      if (!sessionId) {
        logger.debug('创建新会话');
        const newSession = await api.session.create('新对话');
        sessionId = newSession.session_id || newSession.id;
        setCurrentSessionId(sessionId);
        setShowWelcome(false);
        logger.info('新会话创建成功', { sessionId });
      }
      
      // 发送到后端（后端会自动处理树形结构和版本分组）
      await api.message.send(sessionId, messageText, model);
      
      // 重新加载消息列表（从后端获取完整的树形结构）
      const messagesData = await api.session.getMessages(sessionId);
      setMessages(messagesData.messages || []);
      
      const duration = performance.now() - startTime;
      logger.info('消息发送成功', { 
        sessionId, 
        messageCount: messagesData.messages?.length || 0,
        duration: `${duration.toFixed(2)}ms`
      });
      
      // 刷新会话列表
      await loadSessions();
    } catch (error: any) {
      const duration = performance.now() - startTime;
      logger.error('消息发送失败', error as Error, {
        sessionId: currentSessionId,
        messageText: messageText.substring(0, 50),
        model,
        duration: `${duration.toFixed(2)}ms`
      });
      
      // 添加错误消息
      addMessage({
        id: `msg_${Date.now()}_error`,
        session_id: currentSessionId || '',
        role: 'assistant',
        content: `抱歉，发生错误：${error.message || '请稍后重试'}`,
        created_at: new Date().toISOString(),
        agent_type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleMessageEdit = async (messageId: string, newContent: string) => {
    try {
      // 找到消息的索引
      const msgIndex = messages.findIndex(m => m.id === messageId);
      if (msgIndex === -1) return;
      
      // 更新消息内容
      const updatedMessages = [...messages];
      updatedMessages[msgIndex] = {
        ...updatedMessages[msgIndex],
        content: newContent,
      };
      
      // 删除该消息之后的所有消息
      const newMessages = updatedMessages.slice(0, msgIndex + 1);
      setMessages(newMessages);
      
      // 重新发送
      await handleSendMessage(newContent, currentModel);
    } catch (error) {
      console.error('编辑失败:', error);
    }
  };
  
  const handleRegenerate = async (messageId: string) => {
    const msgIndex = messages.findIndex(m => m.id === messageId);
    if (msgIndex === -1 || msgIndex === 0) return;
    
    // 找到上一条用户消息
    const previousUserMsg = messages[msgIndex - 1];
    if (previousUserMsg.role === 'user') {
      // 删除当前消息
      const newMessages = messages.slice(0, msgIndex);
      setMessages(newMessages);
      
      // 重新发送
      await handleSendMessage(previousUserMsg.content, currentModel);
    }
  };
  
  const handleBranch = async (content: string) => {
    handleNewChat();
    // 等待状态更新
    setTimeout(() => {
      handleSendMessage(content, currentModel);
    }, 100);
  };
  
  const handleExampleClick = (prompt: string) => {
    setShowWelcome(false);
    handleSendMessage(prompt, currentModel);
  };
  
  // 使用useMemo缓存messages数组，避免每次渲染都创建新引用
  // 只依赖messages数组本身，React会自动处理引用比较
  const memoizedMessages = useMemo(() => messages, [messages]);
  
  return (
    <div 
      className={`app-container ${sidebarOpen ? 'sidebar-open' : ''}`}
      data-theme={theme}
    >
      <Header />
      
      <div className="container">
        <Sidebar
          onSessionClick={handleSessionClick}
          onNewChat={handleNewChat}
          onSessionAction={handleSessionAction}
        />
        
        <main className="main-content">
          {/* Welcome Screen */}
          {showWelcome && messages.length === 0 && (
            <WelcomeScreen onExampleClick={handleExampleClick} />
          )}
          
          {/* Chat Messages */}
          {!showWelcome || messages.length > 0 ? (
            <div className="chat-messages" id="chatMessages">
              {memoizedMessages.map((msg) => {
                // 只显示根节点（parent_id为null的用户消息）和当前选中版本的助手消息
                // 助手消息的显示由Message组件根据当前版本索引决定
                if (msg.role === 'user' && !msg.parent_id) {
                  // 显示用户消息（根节点）
                  return (
                    <Message
                      key={`user-${msg.id}`}
                      message={msg}
                      messages={memoizedMessages}
                      onEdit={handleMessageEdit}
                      onRegenerate={handleRegenerate}
                      onBranch={handleBranch}
                    />
                  );
                } else if (msg.role === 'assistant') {
                  // 助手消息的显示由Message组件控制（根据parent_id和sibling_index）
                  return (
                    <Message
                      key={`assistant-${msg.id}`}
                      message={msg}
                      messages={memoizedMessages}
                      onEdit={handleMessageEdit}
                      onRegenerate={handleRegenerate}
                      onBranch={handleBranch}
                    />
                  );
                }
                return null;
              })}
              <div ref={messagesEndRef} />
            </div>
          ) : null}
          
          {/* Input Area */}
          <ChatInput
            models={models}
            onSend={handleSendMessage}
            disabled={false}
          />
        </main>
      </div>
    </div>
  );
};

export default App;
