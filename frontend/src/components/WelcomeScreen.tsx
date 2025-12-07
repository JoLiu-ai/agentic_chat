/**
 * WelcomeScreen 组件
 */
import React from 'react';

interface WelcomeScreenProps {
  onExampleClick: (prompt: string) => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onExampleClick }) => {
  const examples = [
    '今天北京天气如何？',
    '写一个快速排序算法',
    '解释一下量子计算',
  ];
  
  return (
    <div className="welcome-screen" id="welcomeScreen">
      <div className="welcome-content">
        <div className="welcome-icon">🤖</div>
        <h2>欢迎使用 Agentic Chat</h2>
        <p>我是一个多Agent智能助手，可以帮你：</p>
        
        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>网络搜索</h3>
            <p>实时获取最新信息</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💻</div>
            <h3>代码执行</h3>
            <p>编写和运行Python代码</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💬</div>
            <h3>智能对话</h3>
            <p>日常交流和问答</p>
          </div>
        </div>
        
        <div className="example-prompts">
          <p className="example-label">试试这些问题：</p>
          {examples.map((example, idx) => (
            <button 
              key={idx}
              className="example-prompt"
              onClick={() => onExampleClick(example)}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

