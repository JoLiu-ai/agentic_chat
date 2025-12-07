# Agentic Chat - 前端应用

前后端分离架构 - 前端部分

## 项目结构

```
frontend/
├── public/              # 静态资源
│   ├── index.html      # HTML 模板
│   └── favicon.ico     # 图标
├── src/
│   ├── api/            # API 调用
│   │   ├── client.ts   # HTTP 客户端
│   │   └── endpoints.ts # API 端点
│   ├── components/     # React 组件
│   ├── pages/          # 页面
│   ├── hooks/          # 自定义 Hooks
│   ├── store/          # 状态管理
│   ├── utils/          # 工具函数
│   ├── App.tsx         # 根组件
│   └── main.tsx        # 入口文件
├── package.json        # 依赖配置
├── vite.config.ts      # Vite 配置
└── README.md           # 本文件

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **状态管理**: Zustand / Redux Toolkit
- **路由**: React Router
- **UI 库**: Ant Design / Material-UI / Tailwind CSS
- **HTTP 客户端**: Axios
- **实时通信**: WebSocket / SSE

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

创建 `.env.local` 文件：

```env
# API 地址
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1

# WebSocket 地址
VITE_WS_URL=ws://localhost:8000/ws

# 其他配置
VITE_APP_TITLE=Agentic Chat
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:3000

### 4. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录

## 部署方案

### 方案 1: Nginx 静态部署

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    root /var/www/frontend/dist;
    index index.html;
    
    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 方案 2: Vercel 部署

```bash
npm install -g vercel
vercel deploy
```

### 方案 3: Docker 部署

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## API 集成

### HTTP 客户端配置

```typescript
// src/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL + '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 错误处理
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default apiClient;
```

### API 调用示例

```typescript
// src/api/endpoints.ts
import apiClient from './client';

export const chatAPI = {
  // 发送消息
  sendMessage: (sessionId: string, message: string) =>
    apiClient.post(`/chat/${sessionId}`, { message }),
  
  // 获取会话列表
  getSessions: () =>
    apiClient.get('/sessions'),
  
  // 创建新会话
  createSession: () =>
    apiClient.post('/sessions'),
};
```

## 开发规范

### 代码风格

- 使用 ESLint + Prettier
- 遵循 Airbnb 风格指南
- TypeScript 严格模式

### 组件规范

```typescript
// components/ChatMessage.tsx
import React from 'react';

interface ChatMessageProps {
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  content,
  role,
  timestamp,
}) => {
  return (
    <div className={`message message-${role}`}>
      <div className="content">{content}</div>
      <div className="timestamp">{timestamp}</div>
    </div>
  );
};
```

## 目录迁移

如果你有现有的 `ui/` 目录，可以这样迁移：

```bash
# 1. 将现有静态文件移动到 public
mv ../ui/static/* public/

# 2. 将 index.html 移动到 public
mv ../ui/index.html public/

# 3. 将 JS 文件改为 TypeScript 并移动到 src
# ... 根据实际情况调整
```

## 常见问题

### Q: CORS 错误？

确保后端配置了正确的 CORS 源：

```python
# backend/.env
CORS_ORIGINS=http://localhost:3000
```

### Q: API 请求 404？

检查 API 基础路径是否正确：

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Q: WebSocket 连接失败？

确保使用正确的协议（ws:// 或 wss://）

## 相关链接

- [React 文档](https://react.dev/)
- [Vite 文档](https://vitejs.dev/)
- [TypeScript 文档](https://www.typescriptlang.org/)

