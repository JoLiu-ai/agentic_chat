"""
网页搜索工具 - 使用Tavily API
"""
import os
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from app.core.config import settings

# 初始化Tavily搜索
def _init_tavily():
    """初始化Tavily搜索实例"""
    if settings.TAVILY_API_KEY:
        os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY
    
    return TavilySearchResults(
        max_results=3,
        search_depth="advanced"
    )

_tavily_instance = _init_tavily()

@tool
def search_web(query: str) -> str:
    """
    搜索网页获取最新信息
    
    Args:
        query: 搜索关键词
        
    Returns:
        搜索结果摘要
    """
    try:
        results = _tavily_instance.invoke({"query": query})
        
        if not results:
            return "未找到相关信息"
        
        # 格式化结果
        formatted = []
        for i, result in enumerate(results[:3], 1):
            formatted.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   来源: {result.get('url', 'N/A')}\n"
                f"   摘要: {result.get('content', 'No content')[:200]}..."
            )
        
        return "\n\n".join(formatted)
        
    except Exception as e:
        return f"搜索失败: {str(e)}"

class SearchTools:
    """搜索工具类 - 提供工具列表"""
    
    def get_tools(self):
        """返回可用工具列表"""
        return [search_web]



# 使用示例
"""
from app.tools.search import SearchTools

search_tools = SearchTools()
tools = search_tools.get_tools()

# 在Agent中绑定工具
model_with_tools = model.bind_tools(tools)
"""