# Agentic Chat - 多Agent智能对话系统

基于 LangGraph 的前后端分离智能对话系统

![Architecture](https://img.shields.io/badge/架构-前后端分离-blue)
![Backend](https://img.shields.io/badge/后端-FastAPI-green)
![Frontend](https://img.shields.io/badge/前端-React%20%2B%20TypeScript-61dafb)
![AI](https://img.shields.io/badge/AI-LangChain%20%2B%20LangGraph-orange)

## 📋 目录结构

```
agentic_chat/
├── backend/                    # 后端服务（FastAPI）
│   ├── app/                   # 应用代码
│   │   ├── api/              # API 路由
│   │   ├── core/             # 核心模块（配置、日志、中间件）
│   │   ├── db/               # 数据库模型
│   │   ├── agents/           # Agent 实现
│   │   ├── services/         # 业务逻辑
│   │   └── main.py           # 应用入口
│   ├── data/                 # 数据库文件
│   ├── logs/                 # 日志文件
│   ├── tests/                # 测试
│   ├── requirements.txt      # Python 依赖
│   └── .env                  # 环境变量
├── frontend/                  # 前端应用（React + TypeScript）
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── api/             # API 调用
│   │   ├── store/           # 状态管理
│   │   ├── utils/           # 工具函数
│   │   └── App.tsx          # 主组件
│   ├── public/              # 静态资源
│   ├── package.json         # 前端依赖
│   └── vite.config.ts       # Vite 配置
├── docs/                     # 文档
├── README.md                 # 本文件
└── start-dev.sh              # 开发环境启动脚本
```

## ✨ 核心特性

### 后端特性

- **🏗️ 生产级架构**
  - 应用工厂模式
  - 模块化设计
  - 前后端完全分离
  
- **🛡️ 完善的中间件栈**
  - CORS 跨域支持
  - 请求 ID 追踪
  - 性能监控和慢查询检测
  - 访问日志（独立文件）
  - API 限流保护
  - 安全响应头
  - Gzip 压缩

- **📊 结构化日志系统**
  - JSON 格式（生产环境）
  - 彩色输出（开发环境）
  - 日志轮转（按时间/大小）
  - 独立的访问日志和错误日志

- **🔧 异常处理**
  - 细化的异常类型
  - 全局异常捕获
  - 结构化错误响应
  - 生产环境隐藏详情

- **💎 优雅关闭**
  - 生命周期管理
  - 数据库连接池
  - 资源清理

### 前端特性

- **⚛️ 现代技术栈**
  - React 18 + TypeScript
  - Vite 5 构建工具
  - Zustand 状态管理

- **🎨 完整功能**
  - 会话管理（创建、删除、重命名、收藏）
  - Markdown 渲染 + 代码高亮
  - 消息编辑和重新生成
  - 版本历史管理
  - Agent 类型显示
  - 引用来源显示
  - 主题切换（亮色/暗色）

- **🚀 开发体验**
  - 热模块替换（HMR）
  - TypeScript 类型检查
  - 组件化架构
  - 响应式布局

## 🚀 快速开始

### 一键启动（最简单）

```bash
# 1. 克隆项目
git clone <repo-url>
cd agentic_chat

# 2. 配置后端环境变量
cd backend
cp .env.example .env
# 编辑 .env，设置 OPENAI_API_KEY=sk-...

# 3. 一键启动前后端
cd ..
./start-dev.sh
```

访问：
- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 手动启动

#### 后端

```bash
cd backend

# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，设置必要的 API Keys

# 4. 启动后端
python -m app.main
# 或使用 uvicorn
uvicorn app.main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.109+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM |
| LangChain | 0.1+ | AI 框架 |
| LangGraph | 0.0.20+ | Agent 编排 |
| Pydantic | 2.5+ | 数据验证 |
| Uvicorn | 0.27+ | ASGI 服务器 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2+ | UI 框架 |
| TypeScript | 5.2+ | 类型系统 |
| Vite | 5.0+ | 构建工具 |
| Zustand | 4.4+ | 状态管理 |
| Axios | 1.6+ | HTTP 客户端 |
| Markdown-it | 14.0+ | Markdown 渲染 |
| Highlight.js | 11.9+ | 代码高亮 |

## 📖 API 文档

启动后端后，访问：http://localhost:8000/docs

### 主要端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/sessions` | GET | 获取会话列表 |
| `/api/v1/sessions` | POST | 创建新会话 |
| `/api/v1/sessions/{id}` | GET | 获取会话详情 |
| `/api/v1/sessions/{id}` | PUT | 更新会话 |
| `/api/v1/sessions/{id}` | DELETE | 删除会话 |
| `/api/v1/chat` | POST | 发送消息 |
| `/api/v1/config/models` | GET | 获取可用模型 |
| `/health` | GET | 健康检查 |
| `/info` | GET | 应用信息 |

## ⚙️ 配置说明

### 后端配置 (`backend/.env`)

```env
# 环境
ENVIRONMENT=development
DEBUG=true

# 服务器
HOST=0.0.0.0
PORT=8000

# 前端地址
FRONTEND_URL=http://localhost:3000

# CORS
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000

# API Keys（必需）
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
OPENAI_MODEL=gpt-4o

# 其他 API（可选）
ANTHROPIC_API_KEY=
TAVILY_API_KEY=

# 限流
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=60/minute

# 数据库
DATABASE_URL=sqlite:///data/agentic_chat.db
```

### 前端配置

前端配置已内置在 `vite.config.ts` 中：
- API 地址：`http://localhost:8000`
- API 版本：`v1`

如需修改，编辑 `frontend/vite.config.ts`。

## 🎯 功能特性

### 多 Agent 系统

- **Router Agent** 🎯 - 路由分发
- **Researcher Agent** 🔍 - 网络搜索
- **Coder Agent** 💻 - 代码生成和执行
- **Assistant Agent** 💬 - 通用对话

### 会话管理

- 创建、删除、重命名会话
- 收藏重要对话
- 按时间分组（今天、昨天、7天内、更早）
- 搜索会话

### 消息功能

- Markdown 渲染
- 代码语法高亮
- 消息编辑和重新生成
- 复制、分享、点赞
- 引用来源显示
- Think 模式切换

### 开发特性

- 热更新（前后端）
- TypeScript 类型安全
- 完整的错误处理
- 性能监控
- 访问日志

## 📚 开发指南

### 后端开发

```bash
cd backend

# 运行测试
pytest

# 代码格式化
black app/
ruff check app/

# 启动开发服务器
python -m app.main
```

### 前端开发

```bash
cd frontend

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 🐛 故障排查

### 后端无法启动

```bash
# 检查 Python 版本
python --version  # 需要 3.8+

# 检查虚拟环境
source backend/.venv/bin/activate

# 检查依赖
pip install -r backend/requirements.txt

# 检查配置
cat backend/.env
```

### 前端无法启动

```bash
# 检查 Node 版本
node --version  # 需要 18+

# 重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
npm install

# 启动
npm run dev
```

### CORS 错误

确保后端配置了正确的前端地址：

```env
# backend/.env
CORS_ORIGINS=http://localhost:3000
```

### API 连接失败

1. 检查后端是否运行：`curl http://localhost:8000/health`
2. 检查 CORS 配置
3. 查看浏览器控制台错误

## 📦 部署

详见：[部署文档](docs/deployment.md)

### Docker Compose 部署

```bash
docker-compose up -d
```

### 独立部署

- **后端**: Uvicorn + Nginx
- **前端**: Nginx 静态托管或 Vercel

## 🧪 测试

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
npm test
```

## 📝 环境变量

### 必需的环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-...` |
| `CORS_ORIGINS` | 允许的前端地址 | `http://localhost:3000` |

### 可选的环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ENVIRONMENT` | `development` | 运行环境 |
| `DEBUG` | `false` | 调试模式 |
| `PORT` | `8000` | 后端端口 |
| `RATE_LIMIT_ENABLED` | `true` | 是否启用限流 |
| `GZIP_ENABLED` | `true` | 是否启用压缩 |

## 🌟 特色功能

### 1. 结构化日志

- **开发环境**：彩色控制台输出
- **生产环境**：JSON 格式（便于 ELK 解析）
- **日志分离**：app.log, error.log, access.log

### 2. 性能监控

- 请求处理时间监控
- 慢请求自动告警
- SQL 慢查询检测
- 响应头包含性能指标

### 3. 安全特性

- CORS 配置
- 安全响应头
- API 限流
- 请求 ID 追踪
- 受信主机验证

### 4. 开发体验

- 热更新（前后端）
- API 自动文档
- TypeScript 类型提示
- 详细的错误信息

## 📖 文档

- [快速开始](QUICKSTART.md) - 5分钟上手
- [部署指南](docs/deployment.md) - 生产部署
- [前端文档](frontend/README.md) - 前端开发
- [API 文档](http://localhost:8000/docs) - 在线 API 文档

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://react.dev/)
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)

---

**开始使用：**

```bash
./start-dev.sh
```

然后访问：http://localhost:3000 🎉

