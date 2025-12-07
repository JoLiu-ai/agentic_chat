/**
 * 前端日志工具
 * 
 * 功能：
 * - 统一的日志格式
 * - 日志级别控制
 * - 错误追踪和堆栈信息
 * - 开发/生产环境区分
 * - 可选的日志上报
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
  error?: Error;
  stack?: string;
}

class Logger {
  private isDevelopment = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEBUG === 'true';
  private logHistory: LogEntry[] = [];
  private maxHistorySize = 100;

  private formatMessage(level: LogLevel, message: string, context?: Record<string, any>, error?: Error): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` | ${JSON.stringify(context)}` : '';
    const errorStr = error ? ` | Error: ${error.message}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${contextStr}${errorStr}`;
  }

  private addToHistory(entry: LogEntry): void {
    this.logHistory.push(entry);
    if (this.logHistory.length > this.maxHistorySize) {
      this.logHistory.shift();
    }
  }

  private log(level: LogLevel, message: string, context?: Record<string, any>, error?: Error): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      error,
      stack: error?.stack,
    };

    this.addToHistory(entry);

    const formattedMessage = this.formatMessage(level, message, context, error);

    // 根据级别输出
    switch (level) {
      case 'debug':
        if (this.isDevelopment) {
          console.debug(`%c${formattedMessage}`, 'color: #888');
        }
        break;
      case 'info':
        console.info(`%c${formattedMessage}`, 'color: #2196F3');
        break;
      case 'warn':
        console.warn(`%c${formattedMessage}`, 'color: #FF9800');
        if (error) {
          console.warn(error);
        }
        break;
      case 'error':
        console.error(`%c${formattedMessage}`, 'color: #F44336; font-weight: bold');
        if (error) {
          console.error('Error details:', error);
          if (error.stack) {
            console.error('Stack trace:', error.stack);
          }
        }
        // 在开发环境显示更多信息
        if (this.isDevelopment && context) {
          console.table(context);
        }
        break;
    }

    // 生产环境可以上报错误到服务器
    if (level === 'error' && !this.isDevelopment) {
      this.reportError(entry);
    }
  }

  /**
   * 上报错误到服务器（可选）
   */
  private async reportError(entry: LogEntry): Promise<void> {
    try {
      // 可以发送到错误收集服务（如 Sentry, LogRocket 等）
      // await fetch('/api/logs/error', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(entry),
      // });
    } catch (err) {
      // 静默失败，避免循环错误
    }
  }

  /**
   * Debug 日志（仅在开发环境显示）
   */
  debug(message: string, context?: Record<string, any>): void {
    this.log('debug', message, context);
  }

  /**
   * Info 日志
   */
  info(message: string, context?: Record<string, any>): void {
    this.log('info', message, context);
  }

  /**
   * Warning 日志
   */
  warn(message: string, context?: Record<string, any>, error?: Error): void {
    this.log('warn', message, context, error);
  }

  /**
   * Error 日志
   */
  error(message: string, error?: Error, context?: Record<string, any>): void {
    this.log('error', message, context, error);
  }

  /**
   * 获取日志历史（用于调试）
   */
  getHistory(): LogEntry[] {
    return [...this.logHistory];
  }

  /**
   * 清空日志历史
   */
  clearHistory(): void {
    this.logHistory = [];
  }

  /**
   * 导出日志历史（用于错误报告）
   */
  exportHistory(): string {
    return JSON.stringify(this.logHistory, null, 2);
  }

  /**
   * 打印日志历史到控制台
   */
  printHistory(): void {
    console.group('📋 Log History');
    this.logHistory.forEach((entry, index) => {
      const style = entry.level === 'error' 
        ? 'color: #F44336' 
        : entry.level === 'warn' 
        ? 'color: #FF9800' 
        : 'color: #2196F3';
      console.log(`%c[${index + 1}] ${entry.timestamp} [${entry.level.toUpperCase()}] ${entry.message}`, style);
      if (entry.context) {
        console.log('Context:', entry.context);
      }
      if (entry.error) {
        console.error(entry.error);
      }
    });
    console.groupEnd();
  }
}

// 创建全局实例
export const logger = new Logger();

// 导出类型
export type { LogLevel, LogEntry };

