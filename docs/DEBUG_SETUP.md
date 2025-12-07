# 调试模式配置指南

本文档说明如何开启前后端的调试模式，以便更好地调试和开发。

## 后端调试模式

### 方法1：使用环境变量（推荐）

创建 `.env` 文件（如果不存在）：

```bash
# 在项目根目录
cp .env.example .env
```

编辑 `.env` 文件，设置以下变量：

```env
# 环境配置
ENVIRONMENT=development
DEBUG=True

# 日志配置
LOG_LEVEL=DEBUG
```

### 方法2：直接修改配置文件

编辑 `backend/app/core/config.py`：

```python
ENVIRONMENT: Environment = Environment.DEVELOPMENT
DEBUG: bool = True
LOG_LEVEL: str = "DEBUG"
```

### 验证调试模式

启动后端后，查看日志输出：

```bash
# 应该看到类似输出
✅ Logging initialized | dir=... | env=development
🚀 Starting Agentic Chat API
🔧 Debug mode: True
```

### 调试功能

启用调试模式后，你将获得：

1. **详细的错误信息**：包括完整的堆栈跟踪
2. **DEBUG级别日志**：所有调试信息都会显示
3. **彩色控制台输出**：更易读的日志格式
4. **API文档**：访问 `http://localhost:8000/docs`

### 查看日志

```bash
# 实时查看所有日志
tail -f backend/logs/app.log

# 实时查看错误日志
tail -f backend/logs/error.log

# 查看DEBUG日志
grep "DEBUG" backend/logs/app.log
```

## 前端调试模式

### 方法1：使用环境变量（推荐）

前端使用 Vite，会自动加载 `.env.development` 文件。

确保 `frontend/.env.development` 存在并包含：

```env
VITE_ENABLE_DEBUG=true
```

### 方法2：在代码中启用

前端日志工具会自动检测开发模式，但你可以强制启用：

```typescript
// 在浏览器控制台执行
localStorage.setItem('debug', 'true');
```

### 验证调试模式

1. 打开浏览器开发者工具（F12）
2. 切换到 Console 标签
3. 应该看到彩色的日志输出，包括：
   - Info: 蓝色
   - Warn: 橙色
   - Error: 红色加粗
   - Debug: 灰色（仅在开发环境）

### 调试功能

启用调试模式后，你将获得：

1. **详细的错误信息**：包括堆栈跟踪
2. **DEBUG日志**：所有调试信息都会显示
3. **日志历史**：可以查看最近的日志记录
4. **性能监控**：操作耗时信息

### 使用日志工具

```typescript
import { logger } from './utils/logger';

// Debug日志（仅在开发环境显示）
logger.debug("调试信息", { data });

// Info日志
logger.info("操作成功", { userId });

// 错误日志（包含堆栈）
logger.error("操作失败", error, { context });

// 查看日志历史
logger.printHistory();

// 导出日志历史
const history = logger.exportHistory();
console.log(history);
```

## 快速启用调试模式

### 一键启用脚本

创建 `enable-debug.sh`：

```bash
#!/bin/bash

# 后端调试配置
cat > .env << EOF
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///data/agentic_chat.db
OPENAI_API_KEY=${OPENAI_API_KEY:-your_key_here}
EOF

# 前端调试配置（如果不存在）
if [ ! -f frontend/.env.development ]; then
    cat > frontend/.env.development << EOF
VITE_ENABLE_DEBUG=true
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
EOF
fi

echo "✅ 调试模式已启用"
echo "📝 后端: DEBUG=True, LOG_LEVEL=DEBUG"
echo "📝 前端: VITE_ENABLE_DEBUG=true"
```

运行：

```bash
chmod +x enable-debug.sh
./enable-debug.sh
```

## 常见问题

### Q: 后端日志还是看不到DEBUG信息？

1. 检查 `.env` 文件是否存在且配置正确
2. 确保重启了后端服务
3. 检查日志级别设置：
   ```python
   # 在 backend/app/core/config.py
   LOG_LEVEL: str = "DEBUG"
   ```

### Q: 前端看不到DEBUG日志？

1. 确保在开发模式下运行（`npm run dev`）
2. 检查浏览器控制台的过滤器设置
3. 确保 `VITE_ENABLE_DEBUG=true` 在 `.env.development` 中

### Q: 如何临时禁用调试模式？

**后端**：
```bash
# 在 .env 中设置
DEBUG=False
LOG_LEVEL=INFO
```

**前端**：
```bash
# 在 .env.development 中设置
VITE_ENABLE_DEBUG=false
```

### Q: 生产环境如何关闭调试？

**后端**：
```env
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

**前端**：
生产构建会自动禁用调试日志。

## 调试技巧

1. **使用Request ID追踪**：后端每个请求都有唯一的request_id
2. **查看日志历史**：前端可以使用 `logger.printHistory()` 查看最近的日志
3. **性能监控**：日志中包含操作耗时信息
4. **错误追踪**：所有错误都包含完整的堆栈信息

## 注意事项

⚠️ **安全提示**：
- 调试模式会暴露详细的错误信息
- 生产环境务必关闭调试模式
- 不要在生产环境使用DEBUG日志级别

