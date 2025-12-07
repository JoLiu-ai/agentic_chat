/**
 * ChatInput 组件 - 输入区域
 */
import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../store';
import { adjustTextareaHeight } from '../utils/helpers';
import { ModelSelector } from './ModelSelector';
import type { Model } from '../types';

interface ChatInputProps {
  models: Model[];
  onSend: (message: string, model: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ models, onSend, disabled }) => {
  const { currentModel, setCurrentModel, thinkMode, setThinkMode, isLoading } = useAppStore();
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  useEffect(() => {
    if (textareaRef.current) {
      adjustTextareaHeight(textareaRef.current);
    }
  }, [message]);
  
  const handleSend = () => {
    if (!message.trim() || isLoading || disabled) return;
    onSend(message.trim(), currentModel);
    setMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  const canSend = message.trim() && !isLoading && !disabled;
  
  return (
    <div className="input-container">
      {/* Thinking Indicator */}
      {isLoading && thinkMode && (
        <div className="thinking-indicator" style={{ display: 'flex' }}>
          <div className="thinking-icon">🤖</div>
          <div className="thinking-text">
            <span>Assistant</span> is thinking
            <span className="thinking-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
        </div>
      )}
      
      <div className="input-wrapper">
        <div className="input-controls-left">
          <button className="input-icon-button" title="附加文件">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 5v14M5 12h14" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
          <button className="input-icon-button" title="格式">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M4 7h16M10 11h10M4 15h16" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>
        
        <textarea
          ref={textareaRef}
          className="message-input"
          placeholder="How can I help you today?"
          rows={1}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading || disabled}
        />
        
        <div className="input-controls-right">
          {/* Think Mode Toggle */}
          <button 
            className="mode-toggle" 
            title="切换模式"
            onClick={() => setThinkMode(!thinkMode)}
          >
            <span className="mode-icon">{thinkMode ? '💡' : '⚡'}</span>
            <span className="mode-text">{thinkMode ? 'Think' : 'Fast'}</span>
          </button>
          
          {/* Model Selector */}
          <ModelSelector
            models={models}
            currentModel={currentModel}
            onModelChange={setCurrentModel}
            disabled={isLoading}
          />
          
          {/* Send Button */}
          <button
            className="send-button"
            onClick={handleSend}
            disabled={!canSend}
            title="发送 (Enter)"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 19V5M5 12l7-7 7 7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
      
      <div className="input-hint">
        <span className="hint-item">
          <kbd>⇧</kbd> + <kbd>↵</kbd> 换行
        </span>
        <span className="hint-separator">·</span>
        <span className="hint-item">
          <kbd>↵</kbd> 发送
        </span>
      </div>
    </div>
  );
};

