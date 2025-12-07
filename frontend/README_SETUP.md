# 前端启动说明

## ⚠️ 重要：环境变量配置

由于 `.env.local` 文件被 gitignore，需要手动创建。

### 快速配置

在 `frontend/` 目录下创建 `.env.local` 文件：

```bash
cd frontend

# 方法 1: 复制示例文件
cp .env.example .env.local

# 方法 2: 直接创建
cat > .env.local << 'EOF'
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_TITLE=Agentic Chat
VITE_APP_DESCRIPTION=多Agent智能对话系统
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
EOF
```

### 或使用临时方案

暂时使用 `.env` 文件（已创建，可以直接使用）：

```bash
# 文件已存在: frontend/.env
# 包含所有必要的环境变量
```

## 启动前端

```bash
# 1. 确保已安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

## 验证

访问: http://localhost:3000

应该看到：
- ✅ 聊天界面
- ✅ 右上角显示"● 已连接"（绿色）

## 故障排查

### 问题 1: 端口被占用

```bash
# 查找占用进程
lsof -i :3000

# 杀死进程
kill -9 <PID>
```

### 问题 2: API 连接失败

检查：
1. 后端是否启动（http://localhost:8000/health）
2. `.env` 或 `.env.local` 配置是否正确
3. CORS 配置是否包含前端地址

### 问题 3: 环境变量未生效

```bash
# 清除缓存
rm -rf node_modules/.vite

# 重启开发服务器
npm run dev
```

## 推荐流程

```bash
# 终端 1: 启动后端
cd /path/to/agentic_chat
python -m app.main

# 终端 2: 启动前端
cd /path/to/agentic_chat/frontend
npm run dev
```

或使用根目录的一键启动脚本：

```bash
# 根目录
./start-dev.sh
```

