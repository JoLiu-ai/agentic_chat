# 🚀 快速开始指南

## 📦 前置要求

- Python 3.8+
- Node.js 18+
- npm 9+

## ⚡ 一键启动（最快）

```bash
# 1. 配置后端 API Key
cd backend
echo 'OPENAI_API_KEY=sk-your-key-here' >> .env
cd ..

# 2. 启动
./start-dev.sh
```

访问：http://localhost:3000 🎉

---

## 📋 详细步骤

### 1. 后端设置

```bash
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置 OPENAI_API_KEY
```

### 2. 前端设置

```bash
cd frontend

# 安装依赖
npm install
```

### 3. 启动服务

#### 方式 A: 使用启动脚本（推荐）

```bash
# 在项目根目录
./start-dev.sh
```

这会自动：
- ✅ 检查环境和依赖
- ✅ 启动后端（http://localhost:8000）
- ✅ 启动前端（http://localhost:3000）
- ✅ 显示实时日志

#### 方式 B: 手动启动

**终端 1 - 后端：**
```bash
cd backend
source .venv/bin/activate
python -m app.main
```

**终端 2 - 前端：**
```bash
cd frontend
npm run dev
```

---

## 🌐 访问地址

启动成功后：

- **前端应用**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ✅ 验证安装

### 检查后端

```bash
curl http://localhost:8000/health
```

应该返回：
```json
{
  "status": "healthy",
  "service": "Agentic Chat",
  "version": "1.0.0"
}
```

### 检查前端

浏览器访问：http://localhost:3000

应该看到：
- ✅ Agentic Chat 界面
- ✅ 左侧会话列表
- ✅ 欢迎屏幕
- ✅ 底部输入框

---

## 🎯 快速测试

1. 访问 http://localhost:3000
2. 点击示例问题（如"今天北京天气如何？"）
3. 查看 AI 回复
4. 测试以下功能：
   - 创建新会话
   - 发送消息
   - 编辑消息
   - 重命名会话
   - 删除会话

---

## 🔧 常见问题

### Q: `OPENAI_API_KEY` 在哪里配置？

**A**: 在 `backend/.env` 文件中：

```bash
cd backend
echo 'OPENAI_API_KEY=sk-your-openai-key' >> .env
```

### Q: 端口被占用怎么办？

**A**: 查找并杀掉占用进程：

```bash
# macOS/Linux
lsof -ti :8000 | xargs kill -9  # 后端
lsof -ti :3000 | xargs kill -9  # 前端

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Q: 前端连接不上后端？

**A**: 检查 CORS 配置：

```bash
# backend/.env
CORS_ORIGINS=http://localhost:3000
```

### Q: 依赖安装失败？

**A**: 使用国内镜像：

```bash
# Python
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Node
npm install --registry=https://registry.npmmirror.com
```

---

## 📁 目录说明

```
agentic_chat/
├── backend/          # 后端目录
│   ├── app/         # Python 代码
│   ├── data/        # SQLite 数据库
│   ├── logs/        # 日志文件
│   └── .env         # 后端配置
├── frontend/         # 前端目录
│   ├── src/         # React 代码
│   └── .env.local   # 前端配置（可选）
└── start-dev.sh      # 启动脚本
```

---

## 🎓 下一步

1. **配置 API Keys** - 在 `backend/.env` 中
2. **启动服务** - 运行 `./start-dev.sh`
3. **开始聊天** - 访问 http://localhost:3000
4. **查看文档** - 阅读 [README.md](README.md)
5. **部署上线** - 参考 [部署指南](docs/deployment.md)

---

## 💡 提示

- 使用 **Ctrl+C** 停止所有服务
- 日志文件在 `backend/logs/` 目录
- 开发时代码修改会自动热更新
- API 文档支持在线测试接口

---

**祝使用愉快！** 🎉

有问题查看：[完整文档](README.md) | [部署指南](docs/deployment.md)

