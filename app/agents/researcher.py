"""
研究员Agent - 配备网页搜索工具
"""
from app.agents.base import BaseAgent
from app.tools.search import SearchTools
from langchain_openai import ChatOpenAI

def get_researcher_agent(model: ChatOpenAI):
    """创建配备搜索工具的研究员Agent"""
    search_tools = SearchTools()
    
    return BaseAgent(
        name="researcher",
        model=model,
        system_prompt=(
            "你是一名专业的研究员。你的任务是:\n"
            "1. 使用搜索工具获取最新、准确的信息\n"
            "2. 综合多个来源，给出全面的答案\n"
            "3. 引用信息来源，确保可信度\n\n"
            "当用户询问需要实时信息的问题时，务必调用search_web工具。"
        ),
        tools=search_tools.get_tools()
    )

