/**
 * HTTP 客户端配置
 */
import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';
const API_TIMEOUT = 30000;

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加 token（如果存在）
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加 request-id
    if (config.headers) {
      config.headers['X-Request-ID'] = generateRequestId();
    }
    
    // 开发环境日志
    if (import.meta.env.DEV) {
      console.log('→ API Request:', config.method?.toUpperCase(), config.url, config.data);
    }
    
    return config;
  },
  (error: AxiosError) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 开发环境日志
    if (import.meta.env.DEV) {
      console.log('← API Response:', response.config.url, response.status, response.data);
    }
    
    return response.data;
  },
  (error: AxiosError<any>) => {
    // 错误处理
    if (error.response) {
      const { status, data } = error.response;
      
      // 统一错误处理
      const errorMessage = data?.detail || data?.message || '请求失败';
      
      console.error(`API Error [${status}]:`, errorMessage);
      
      // 返回格式化的错误
      return Promise.reject({
        status,
        message: errorMessage,
        requestId: error.response.headers['x-request-id'],
        ...data,
      });
    }
    
    // 网络错误
    if (error.request) {
      console.error('Network Error:', error.message);
      return Promise.reject({
        message: '网络错误，请检查网络连接',
      });
    }
    
    // 其他错误
    console.error('Error:', error.message);
    return Promise.reject({
      message: error.message || '未知错误',
    });
  }
);

// 生成请求ID
function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export default apiClient;
