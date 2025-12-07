/**
 * ModelSelector 组件 - 分页格式的模型选择器
 */
import React, { useState, useRef, useEffect } from 'react';
import type { Model } from '../types';

interface ModelSelectorProps {
  models: Model[];
  currentModel: string;
  onModelChange: (model: string) => void;
  disabled?: boolean;
}

const ITEMS_PER_PAGE = 6; // 每页显示6个模型

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  currentModel,
  onModelChange,
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // 计算总页数
  const totalPages = Math.ceil(models.length / ITEMS_PER_PAGE);
  const startIndex = currentPage * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const currentPageModels = models.slice(startIndex, endIndex);

  // 获取当前选中的模型标签
  const currentModelLabel = models.find(m => m.value === currentModel)?.label || currentModel;

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleModelSelect = (modelValue: string) => {
    onModelChange(modelValue);
    setIsOpen(false);
    setCurrentPage(0); // 重置到第一页
  };

  const handlePreviousPage = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  if (models.length === 0) {
    return (
      <div className="model-selector-wrapper">
        <div className="model-selector-trigger" style={{ opacity: 0.6 }}>
          加载中...
        </div>
      </div>
    );
  }

  return (
    <div className="model-selector-wrapper" ref={dropdownRef}>
      <div
        className={`model-selector-trigger ${isOpen ? 'active' : ''}`}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        style={{ cursor: disabled ? 'not-allowed' : 'pointer' }}
      >
        <span className="model-selector-label">{currentModelLabel}</span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          stroke="currentColor"
          className={`model-selector-arrow ${isOpen ? 'open' : ''}`}
        >
          <path d="M3 4.5L6 7.5L9 4.5" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>

      {isOpen && (
        <div className="model-selector-dropdown">
          <div className="model-selector-header">
            <span className="model-selector-title">选择模型</span>
            <span className="model-selector-page-info">
              {currentPage + 1} / {totalPages}
            </span>
          </div>

          <div className="model-selector-grid">
            {currentPageModels.map((model) => (
              <div
                key={model.value}
                className={`model-selector-item ${
                  model.value === currentModel ? 'selected' : ''
                }`}
                onClick={() => handleModelSelect(model.value)}
              >
                <div className="model-selector-item-label">{model.label}</div>
                {model.value === currentModel && (
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                    className="model-selector-check"
                  >
                    <path
                      d="M13.5 4.5L6 12L2.5 8.5"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="model-selector-pagination">
              <button
                className="model-selector-page-btn"
                onClick={handlePreviousPage}
                disabled={currentPage === 0}
                title="上一页"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor">
                  <path d="M10 12L6 8L10 4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              <div className="model-selector-page-dots">
                {Array.from({ length: totalPages }).map((_, index) => (
                  <div
                    key={index}
                    className={`model-selector-dot ${index === currentPage ? 'active' : ''}`}
                    onClick={() => setCurrentPage(index)}
                  />
                ))}
              </div>
              <button
                className="model-selector-page-btn"
                onClick={handleNextPage}
                disabled={currentPage === totalPages - 1}
                title="下一页"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor">
                  <path d="M6 4L10 8L6 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

