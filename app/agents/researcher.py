from app.agents.base import BaseAgent
from app.tools.search import get_search_tool
from langchain_openai import ChatOpenAI

def get_researcher_agent(model: ChatOpenAI):
    search_tool = get_search_tool()
    
    return BaseAgent(
        name="researcher",
        model=model,
        system_prompt="You are a researcher. You search for information using the available tools and provide detailed answers based on the search results.",
        tools=[search_tool]
    )
