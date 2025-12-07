# 日志使用指南

本文档说明如何在前后端使用日志系统进行调试和错误追踪。

## 后端日志

### 基本使用

后端已经配置了完整的日志系统，使用 Python 的 `logging` 模块。

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# 不同级别的日志
logger.debug("调试信息")  # 仅在DEBUG模式下显示
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 记录异常

```python
try:
    # 你的代码
    result = some_operation()
except Exception as e:
    # 方式1：使用 exc_info=True 记录完整堆栈
    logger.error(f"操作失败: {e}", exc_info=True)
    
    # 方式2：使用 logger.exception() 自动包含堆栈
    logger.exception("操作失败")
```

### 带上下文的日志

```python
# 添加额外信息
logger.info(
    "用户登录",
    extra={
        "user_id": user_id,
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
)
```

### 日志文件位置

- **应用日志**: `backend/logs/app.log`
- **错误日志**: `backend/logs/error.log`
- **访问日志**: `backend/logs/access.log`

### 查看日志

```bash
# 实时查看应用日志
tail -f backend/logs/app.log

# 实时查看错误日志
tail -f backend/logs/error.log

# 查看最近的错误
tail -n 100 backend/logs/error.log

# 搜索特定错误
grep "ERROR" backend/logs/error.log
```

### 在代码中添加日志示例

```python
# 在 API 端点中
@router.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"收到聊天请求: session_id={request.session_id}")
    
    try:
        # 业务逻辑
        result = process_chat(request)
        logger.info(f"聊天处理成功: session_id={request.session_id}")
        return result
    except Exception as e:
        logger.error(
            f"聊天处理失败: session_id={request.session_id}",
            exc_info=True,
            extra={"request": request.dict()}
        )
        raise

# 在服务层中
class MessageService:
    @staticmethod
    def create_message(...):
        logger.debug(f"创建消息: session_id={session_id}, role={role}")
        
        try:
            # 数据库操作
            message = Message(...)
            db.add(message)
            db.commit()
            logger.info(f"消息创建成功: message_id={message.message_id}")
            return message.message_id
        except Exception as e:
            logger.error(f"消息创建失败: {e}", exc_info=True)
            raise
```

## 前端日志

### 基本使用

前端使用统一的 `logger` 工具。

```typescript
import { logger } from '../utils/logger';

// 不同级别的日志
logger.debug("调试信息");  // 仅在开发环境显示
logger.info("一般信息");
logger.warn("警告信息");
logger.error("错误信息");
```

### 记录错误

```typescript
try {
    await api.message.send(sessionId, message);
} catch (error) {
    // 方式1：自动提取错误信息
    logger.error("发送消息失败", error as Error, {
        sessionId,
        message: message.substring(0, 50)
    });
    
    // 方式2：自定义错误消息
    logger.error("发送消息失败", error as Error, {
        sessionId,
        errorMessage: error.message,
        stack: error.stack
    });
}
```

### 带上下文的日志

```typescript
logger.info("用户操作", {
    action: "send_message",
    sessionId: sessionId,
    messageLength: message.length,
    timestamp: new Date().toISOString()
});
```

### 查看日志

前端日志会输出到浏览器控制台：

1. **打开开发者工具**: `F12` 或 `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
2. **切换到 Console 标签**
3. **查看不同级别的日志**:
   - Info: 蓝色
   - Warn: 橙色
   - Error: 红色加粗

### 日志历史

```typescript
// 获取日志历史
const history = logger.getHistory();
console.log(history);

// 打印日志历史
logger.printHistory();

// 导出日志历史（用于错误报告）
const historyJson = logger.exportHistory();
console.log(historyJson);

// 清空日志历史
logger.clearHistory();
```

### 在代码中添加日志示例

```typescript
// 在 API 调用中
const handleSendMessage = async (messageText: string, model: string) => {
    logger.info("发送消息", { messageText, model });
    
    try {
        setLoading(true);
        const response = await api.message.send(sessionId, messageText, model);
        logger.info("消息发送成功", { sessionId, messageId: response.message_id });
        return response;
    } catch (error) {
        logger.error("消息发送失败", error as Error, {
            sessionId,
            messageText,
            model
        });
        throw error;
    } finally {
        setLoading(false);
    }
};

// 在组件中
useEffect(() => {
    logger.debug("组件挂载", { componentName: "ChatPage" });
    
    const loadData = async () => {
        try {
            logger.info("加载会话列表");
            const data = await api.session.list();
            logger.info("会话列表加载成功", { count: data.sessions.length });
            setSessions(data.sessions);
        } catch (error) {
            logger.error("加载会话列表失败", error as Error);
        }
    };
    
    loadData();
    
    return () => {
        logger.debug("组件卸载", { componentName: "ChatPage" });
    };
}, []);
```

## 调试技巧

### 1. 使用日志追踪请求流程

**后端**:
```python
logger.info("请求开始", extra={"request_id": request_id, "path": request.url.path})
# ... 处理逻辑 ...
logger.info("请求完成", extra={"request_id": request_id, "duration": duration})
```

**前端**:
```typescript
logger.info("API请求开始", { endpoint: "/api/chat", method: "POST" });
const response = await api.message.send(...);
logger.info("API请求完成", { endpoint: "/api/chat", duration: Date.now() - startTime });
```

### 2. 使用 Request ID 追踪

后端会自动为每个请求生成 `request_id`，可以在日志中看到：

```
2024-01-01 10:00:00 | INFO | [abc12345] app.api.v1.endpoints.chat | 收到聊天请求
```

前端可以在错误日志中包含这个 ID：

```typescript
catch (error) {
    logger.error("请求失败", error as Error, {
        requestId: error.response?.data?.request_id,
        url: error.config?.url
    });
}
```

### 3. 条件日志

**后端**:
```python
if settings.DEBUG:
    logger.debug(f"详细调试信息: {complex_data}")
```

**前端**:
```typescript
if (import.meta.env.DEV) {
    logger.debug("开发环境调试信息", { data });
}
```

### 4. 性能监控

**后端**:
```python
import time

start_time = time.time()
# ... 操作 ...
duration = time.time() - start_time
logger.info(f"操作耗时: {duration:.3f}s", extra={"duration": duration})
```

**前端**:
```typescript
const startTime = performance.now();
await someAsyncOperation();
const duration = performance.now() - startTime;
logger.info("操作完成", { duration: `${duration.toFixed(2)}ms` });
```

## 常见问题

### Q: 如何只查看错误日志？

**后端**:
```bash
grep "ERROR" backend/logs/error.log
```

**前端**:
在浏览器控制台中使用过滤器，选择 "Errors" 或 "Warnings"

### Q: 如何查看特定会话的日志？

**后端**:
```bash
grep "session_123" backend/logs/app.log
```

**前端**:
```typescript
logger.info("会话操作", { sessionId: "session_123", action: "..." });
```

### Q: 生产环境如何查看日志？

- 后端日志文件在服务器上
- 前端错误可以上报到日志收集服务（如 Sentry）
- 可以使用日志聚合工具（如 ELK Stack）

## 最佳实践

1. **使用合适的日志级别**
   - `debug`: 详细的调试信息
   - `info`: 一般信息（请求、操作成功等）
   - `warn`: 警告（可恢复的错误）
   - `error`: 错误（需要关注的问题）

2. **包含足够的上下文**
   - 请求 ID
   - 用户 ID
   - 操作类型
   - 相关数据（不要记录敏感信息）

3. **记录异常时包含堆栈**
   - 后端: 使用 `exc_info=True` 或 `logger.exception()`
   - 前端: 传递 `Error` 对象

4. **不要记录敏感信息**
   - 密码、token、API key 等

5. **结构化日志**
   - 使用 `extra` 参数（后端）或 `context` 对象（前端）
   - 便于搜索和分析

