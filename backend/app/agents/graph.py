"""
LangGraph 工作流定义 - 多Agent路由系统

架构:
    用户输入
       ↓
    Router (路由决策)
       ↓
    ├─→ Researcher → Tools (搜索) → Researcher → END
    ├─→ Coder → Tools (代码执行) → Coder → END  
    └─→ General → END
"""
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.agents.state import AgentState
from app.agents.base import BaseAgent
from app.agents.router import RouterAgent
from app.agents.researcher import get_researcher_agent
from app.agents.coder import get_coder_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from app.core.config import settings

# 初始化模型 - 使用配置
llm_kwargs = {
    "model": settings.OPENAI_MODEL,
    "temperature": 0,
    "api_key": settings.OPENAI_API_KEY,
}
if settings.OPENAI_BASE_URL:
    llm_kwargs["base_url"] = settings.OPENAI_BASE_URL

llm = ChatOpenAI(**llm_kwargs)

# 初始化Agents
router_agent = RouterAgent(model=llm)
researcher_agent = get_researcher_agent(model=llm)
coder_agent = get_coder_agent(model=llm)
general_agent = BaseAgent(
    name="general_assistant",
    model=llm,
    system_prompt=(
        "你是一个友好、博学的AI助手。你擅长:\n"
        "- 日常对话和闲聊\n"
        "- 创意写作（诗歌、故事、文案）\n"
        "- 知识解答（科学、历史、文化）\n"
        "- 提供建议和意见\n\n"
        "请用友好、专业的语气回答用户问题。"
    )
)

# 创建工具节点
researcher_tools = ToolNode(researcher_agent.tools)
coder_tools = ToolNode(coder_agent.tools)

# 定义Graph
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("router", router_agent)
workflow.add_node("researcher", researcher_agent)
workflow.add_node("researcher_tools", researcher_tools)
workflow.add_node("coder", coder_agent)
workflow.add_node("coder_tools", coder_tools)
workflow.add_node("general_assistant", general_agent)

# 路由逻辑：从router到specialized agents
def route_after_router(state: AgentState):
    """Router决策后的路由"""
    return state["next"]

workflow.set_entry_point("router")
workflow.add_conditional_edges(
    "router",
    route_after_router,
    {
        "researcher": "researcher",
        "coder": "coder",
        "general_assistant": "general_assistant"
    }
)

# Researcher工作流：检查是否需要调用工具
def should_continue_researcher(state: AgentState):
    """检查Researcher是否需要调用工具"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 如果有工具调用，则执行工具
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "end"

workflow.add_conditional_edges(
    "researcher",
    should_continue_researcher,
    {
        "tools": "researcher_tools",
        "end": END
    }
)

# 工具执行后返回给researcher
workflow.add_edge("researcher_tools", "researcher")

# Coder工作流：检查是否需要调用工具
def should_continue_coder(state: AgentState):
    """检查Coder是否需要调用工具"""
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "end"

workflow.add_conditional_edges(
    "coder",
    should_continue_coder,
    {
        "tools": "coder_tools",
        "end": END
    }
)

workflow.add_edge("coder_tools", "coder")

# General assistant直接结束
workflow.add_edge("general_assistant", END)

# 编译Graph
graph = workflow.compile()

# 测试用例
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    
    test_cases = [
        "今天北京天气如何？",  # Should route to researcher
        "写一个计算斐波那契数列的函数",  # Should route to coder
        "你好，介绍一下你自己",  # Should route to general
    ]
    
    for query in test_cases:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        inputs = {"messages": [HumanMessage(content=query)]}
        result = graph.invoke(inputs)
        
        print(f"\nResponse: {result['messages'][-1].content}")

