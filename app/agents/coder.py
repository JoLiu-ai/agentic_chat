from app.agents.base import BaseAgent
from app.tools.code_executor import get_code_executor_tool
from langchain_openai import ChatOpenAI

def get_coder_agent(model: ChatOpenAI):
    code_tool = get_code_executor_tool()
    
    return BaseAgent(
        name="coder",
        model=model,
        system_prompt="You are a coder. You write and execute Python code to solve problems. Always check the output of your code.",
        tools=[code_tool]
    )
