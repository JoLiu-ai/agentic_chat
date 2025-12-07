/**
 * Header 组件
 */
import React from 'react';
import { useAppStore } from '../store';

export const Header: React.FC = () => {
  const { theme, setTheme, toggleSidebar } = useAppStore();
  
  const handleThemeToggle = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };
  
  return (
    <header className="header">
      <div className="header-left">
        <button 
          className="menu-toggle" 
          id="menuToggle" 
          aria-label="Toggle menu"
          onClick={toggleSidebar}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M3 12h18M3 6h18M3 18h18" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </button>
        <h1 className="logo">
          <span className="logo-icon">🤖</span>
          <span className="logo-text">Agentic Chat</span>
        </h1>
      </div>
      <div className="header-right">
        <button 
          className="icon-button" 
          id="themeToggle" 
          aria-label="Toggle theme"
          onClick={handleThemeToggle}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="5" />
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
          </svg>
        </button>
        <button className="icon-button" id="settingsButton" aria-label="Settings">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 1v6m0 6v10" />
          </svg>
        </button>
      </div>
    </header>
  );
};

