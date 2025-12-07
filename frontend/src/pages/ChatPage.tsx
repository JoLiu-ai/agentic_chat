import React, { useState, useEffect, useRef } from 'react';
import { Card, Input, Button, List, Space, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { api, Message } from '../api/endpoints';

const { TextArea } = Input;

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 初始化会话
  useEffect(() => {
    const initSession = async () => {
      try {
        const session = await api.session.create('新对话');
        setSessionId(session.id);
      } catch (error) {
        message.error('创建会话失败');
        console.error(error);
      }
    };

    initSession();
  }, []);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() || !sessionId) return;

    const userMessage = inputValue;
    setInputValue('');
    setLoading(true);

    // 添加用户消息
    const tempUserMsg: Message = {
      id: Date.now().toString(),
      session_id: sessionId,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      // 发送到后端
      const response = await api.message.send(sessionId, {
        message: userMessage,
      });

      // 添加助手回复
      setMessages((prev) => [...prev, response.message]);
    } catch (error: any) {
      message.error(error.message || '发送失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <Card 
        title="对话窗口" 
        style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}
      >
        <div style={{ flex: 1, overflowY: 'auto', marginBottom: 16 }}>
          <List
            dataSource={messages}
            renderItem={(msg) => (
              <List.Item
                style={{
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  border: 'none',
                }}
              >
                <div
                  style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    background: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                    color: msg.role === 'user' ? 'white' : '#333',
                  }}
                >
                  <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {msg.content}
                  </div>
                  <div
                    style={{
                      fontSize: '12px',
                      marginTop: '4px',
                      opacity: 0.7,
                    }}
                  >
                    {new Date(msg.created_at).toLocaleTimeString()}
                  </div>
                </div>
              </List.Item>
            )}
          />
          <div ref={messagesEndRef} />
        </div>

        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="输入消息... (Enter发送, Shift+Enter换行)"
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={loading || !sessionId}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            disabled={!inputValue.trim() || !sessionId}
          >
            发送
          </Button>
        </Space.Compact>
      </Card>
    </div>
  );
};

