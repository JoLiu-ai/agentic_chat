# 部署指南 - 前后端分离架构

## 架构概览

```
┌─────────────────┐         ┌──────────────────┐
│   前端应用       │         │    后端 API      │
│   (React)       │ ◄────► │   (FastAPI)      │
│   Port: 3000    │         │   Port: 8000     │
└─────────────────┘         └──────────────────┘
        │                           │
        ▼                           ▼
   Nginx/CDN                   Gunicorn/Uvicorn
```

## 后端部署

### 方式 1: Docker 部署（推荐）

```bash
# 1. 构建镜像
docker build -t agentic-chat-api .

# 2. 运行容器
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e CORS_ORIGINS=https://your-frontend.com \
  -e SERVE_STATIC=false \
  --name agentic-chat-api \
  agentic-chat-api
```

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY app/ ./app/
COPY .env.production .env

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 方式 2: Systemd 服务

```bash
# 1. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 创建服务文件
sudo nano /etc/systemd/system/agentic-chat-api.service
```

**/etc/systemd/system/agentic-chat-api.service**:
```ini
[Unit]
Description=Agentic Chat API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/agentic-chat
Environment="PATH=/var/www/agentic-chat/venv/bin"
ExecStart=/var/www/agentic-chat/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 3. 启动服务
sudo systemctl enable agentic-chat-api
sudo systemctl start agentic-chat-api
sudo systemctl status agentic-chat-api
```

### 环境变量配置

创建 `.env.production`:

```env
# 环境
ENVIRONMENT=production
DEBUG=false

# 服务器
HOST=0.0.0.0
PORT=8000

# 前端地址
FRONTEND_URL=https://your-frontend.com

# CORS
CORS_ENABLED=true
CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com

# 安全
ALLOWED_HOSTS=your-api.com,www.your-api.com
SERVE_STATIC=false

# 功能
DOCS_ENABLED=false
OPENAPI_ENABLED=false

# 限流
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute

# 数据库
DATABASE_URL=postgresql://user:pass@localhost/dbname

# API Keys
OPENAI_API_KEY=sk-...
```

## 前端部署

### 方式 1: Nginx 静态部署（推荐）

```bash
# 1. 构建前端
cd frontend
npm install
npm run build

# 2. 部署到 Nginx
sudo cp -r dist/* /var/www/agentic-chat-frontend/
```

**/etc/nginx/sites-available/agentic-chat**:
```nginx
server {
    listen 80;
    server_name your-frontend.com www.your-frontend.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-frontend.com www.your-frontend.com;
    
    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/your-frontend.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-frontend.com/privkey.pem;
    
    # 前端静态文件
    root /var/www/agentic-chat-frontend;
    index index.html;
    
    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
    
    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API 代理（可选，也可以直接连后端）
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# 3. 启用站点
sudo ln -s /etc/nginx/sites-available/agentic-chat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 方式 2: Vercel 部署（最简单）

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 登录
vercel login

# 3. 部署
cd frontend
vercel
```

**vercel.json**:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-api.com/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 方式 3: Docker 部署

**frontend/Dockerfile**:
```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**frontend/nginx.conf**:
```nginx
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
    }
}
```

## Docker Compose 完整部署

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # 后端 API
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - CORS_ORIGINS=http://localhost:3000
      - DATABASE_URL=postgresql://postgres:password@db:5432/agentic_chat
    env_file:
      - .env.production
    depends_on:
      - db
    restart: unless-stopped
  
  # 前端
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
  
  # 数据库
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=agentic_chat
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## SSL 证书配置（Let's Encrypt）

```bash
# 1. 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 2. 获取证书
sudo certbot --nginx -d your-frontend.com -d www.your-frontend.com
sudo certbot --nginx -d your-api.com -d www.your-api.com

# 3. 自动续期
sudo certbot renew --dry-run
```

## 监控和日志

### 后端日志

```bash
# 查看日志
tail -f logs/app.log
tail -f logs/error.log
tail -f logs/access.log

# Systemd 日志
sudo journalctl -u agentic-chat-api -f
```

### Nginx 日志

```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 性能优化

### 后端

- 使用 Gunicorn + Uvicorn workers
- 启用 Redis 缓存
- 数据库连接池
- CDN 加速静态资源

### 前端

- 代码分割（Code Splitting）
- Tree Shaking
- 图片懒加载
- CDN 部署
- Service Worker 缓存

## 安全检查清单

- [ ] HTTPS 启用
- [ ] CORS 配置正确
- [ ] API 密钥安全存储
- [ ] 限流启用
- [ ] 安全响应头配置
- [ ] SQL 注入防护
- [ ] XSS 防护
- [ ] CSRF 防护
- [ ] 日志监控
- [ ] 定期备份

## 故障排查

### 前端无法连接后端

```bash
# 检查 CORS 配置
curl -I https://your-api.com/api/v1/health

# 检查网络
ping your-api.com
```

### 后端 502 错误

```bash
# 检查后端服务
sudo systemctl status agentic-chat-api

# 检查端口
sudo netstat -tlnp | grep 8000
```

## 相关文档

- [前端 README](../frontend/README.md)
- [后端 API 文档](https://your-api.com/docs)

