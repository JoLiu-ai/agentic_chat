"""
路由Agent - 智能分发用户请求到专业Agent
"""
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.agents.state import AgentState
from pydantic import BaseModel, Field  # 使用pyd antic v2

# 定义路由输出结构
class RouteResponse(BaseModel):
    next: Literal["researcher", "coder", "general_assistant"] = Field(
        ..., 
        description="下一个处理请求的Agent"
    )
    reasoning: str = Field(
        ...,
        description="路由决策的理由"
    )

class RouterAgent:
    def __init__(self, model: ChatOpenAI):
        self.model = model
        self.system_prompt = (
            "你是一个智能路由器，负责将用户请求分发给最合适的专业Agent。\n\n"
            "可用的Agent:\n"
            "1. researcher (研究员)\n"
            "   - 适用场景: 需要搜索最新信息、查询事实、了解实时动态\n"
            "   - 示例: '今天天气如何?', '特朗普最新政策', 'AI发展趋势'\n\n"
            "2. coder (程序员)\n"
            "   - 适用场景: 编写代码、调试错误、算法问题\n"
            "   - 示例: '写一个快速排序', '这段代码为什么报错?', '实现斐波那契'\n\n"
            "3. general_assistant (通用助手)\n"
            "   - 适用场景: 日常对话、创意写作、一般性问答\n"
            "   - 示例: '你好', '写一首诗', '解释相对论'\n\n"
            "决策规则:\n"
            "- 如果包含'搜索'、'查询'、'最新'、'今天'等关键词 → researcher\n"
            "- 如果包含'代码'、'编程'、'debug'、'实现'、'算法' → coder\n"
            "- 其他情况 → general_assistant\n\n"
            "请分析用户意图，选择最合适的Agent，并简要说明理由。"
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # 绑定结构化输出
        self.runnable = self.prompt | self.model.with_structured_output(RouteResponse)

    def __call__(self, state: AgentState):
        messages = state["messages"]
        response = self.runnable.invoke({"messages": messages})
        
        # 记录路由决策（用于调试）
        print(f"🔀 Router Decision: {response.next} | Reason: {response.reasoning}")
        
        # 保存到数据库（用于监控）
        try:
            from app.api.v1.endpoints.router_monitor import log_route_decision
            user_message = messages[-1].content if messages else ""
            # 从state中获取session_id（如果有）
            session_id = state.get("session_id", "unknown")
            log_route_decision(
                session_id=session_id,
                user_message=user_message,
                routed_to=response.next,
                reasoning=response.reasoning
            )
        except Exception as e:
            print(f"⚠️  Failed to log route decision: {e}")
        
        return {"next": response.next}

